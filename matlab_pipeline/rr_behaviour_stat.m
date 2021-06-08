function [Bonsai_Event_text, RR]=rr_behaviour_stat(csv)

%Read in csv
Bonsai_Event_csv = dlmread(csv,' ');
Bonsai_Event_timestamp=Bonsai_Event_csv(:,1);
Bonsai_Event=Bonsai_Event_csv(:,2);

%Read in bonsai event codes
% bonsai_event_map = readtable('Bonsai_Event_Codes_RR.xlsx');
data=load('bonsai_event_map.mat');
bonsai_event_map=data.bonsai_event_map;
Bonsai_Event_text=bonsai_event_map(Bonsai_Event,1);
Bonsai_Event_text{:,2}=(Bonsai_Event_timestamp-Bonsai_Event_timestamp(1))/1000;
Bonsai_Event_text{:,3}=Bonsai_Event;

% Reward Offer Tone
R1_0_offer=17;
R1_20_offer=18;
R1_80_offer=19;
R1_100_offer=20;
R2_0_offer=29;
R2_20_offer=30;
R2_80_offer=31;
R2_100_offer=32;
R3_0_offer=41;
R3_20_offer=42;
R3_80_offer=43;
R3_100_offer=44;
R4_0_offer=53;
R4_20_offer=54;
R4_80_offer=55;
R4_100_offer=56;

%Reward Taken
R1_reward_taken=16;
R2_reward_taken=28;
R3_reward_taken=40;
R4_reward_taken=52;

RR_reward_taken_code=[R1_reward_taken R2_reward_taken R3_reward_taken R4_reward_taken];
RR_offer_code=[R1_0_offer R1_20_offer R1_80_offer R1_100_offer;...
    R2_0_offer R2_20_offer R2_80_offer R2_100_offer;...
    R3_0_offer R3_20_offer R3_80_offer R3_100_offer;...
    R4_0_offer R4_20_offer R4_80_offer R4_100_offer];
RR_offer_code_r_num=[1 1 1 1;2 2 2 2; 3 3 3 3; 4 4 4 4];
RR_offer_code_tone_num=[1 2 3 4;1 2 3 4;1 2 3 4;1 2 3 4];
RR_Rwd_omission_code=[15 27 39 51]; % reward not taken

%Servo Opening/Closing
Servo_opened_code=[1 3 5 7];
Servo_closed_code=[2 4 6 8];
Enter_Rx_code=[11 23 35 47];
Reject_Rx_code=[12 24 36 48];
Quit_Rx_code=[13 25 37 49];
TJ_entry_code=[61 64 67 70];
sharp_accept_code=[62 65 68 71];
sharp_exit_code=[63 66 69 72];
NoRwd_sound_code=[15 27 39 51];

%Find offer Award Index
RR_offer_idx=find(ismember(Bonsai_Event,RR_offer_code(:))); %find index of reward offer tones
RR_offer_Event=Bonsai_Event(RR_offer_idx); % get RR offer events
RR.offer_timestamp=Bonsai_Event_timestamp(RR_offer_idx);
[LIA, LIB]=ismember(RR_offer_Event,RR_offer_code);
RR.offer_r_num=RR_offer_code_r_num(LIB);
RR.offer_tone_num=RR_offer_code_tone_num(LIB);
% RR.offer_outcome: 1:reward taken, 2:reward not taken, 3:Accept No reward,
% 4: Quit, 5: Rejection
RR.offer_outcome=RR_offer_Event.*NaN;
RR.offer_dont_use=RR.offer_timestamp.*NaN;
RR.TJ_entry_timestamp=RR.offer_timestamp.*NaN;
RR.quit_timestamp=RR.offer_timestamp.*NaN;
RR.reject_timestamp=RR.offer_timestamp.*NaN;
RR.accept_timestamp=RR.offer_timestamp.*NaN;
RR.sharp_accept_timestamp=RR.offer_timestamp.*NaN;
RR.sharp_exit_timestamp=RR.offer_timestamp.*NaN;
RR.servo_open_timestamp=RR.offer_timestamp.*NaN;
RR.reward_taken_timestamp=RR.offer_timestamp.*NaN;
RR.NoRwd_sound_timestamp=RR.offer_timestamp.*NaN;

r_num = 4;
tone_num=4;
reward_taken=zeros(r_num,tone_num);
reward_avaiable=zeros(r_num,tone_num);
reward_omission=zeros(r_num,tone_num);
quit=zeros(r_num,tone_num);
reject=zeros(r_num,tone_num);

for r=1:r_num
    servo_closed_idx{r}=find(Bonsai_Event==Servo_closed_code(r)); % find servo closed events
    quit_idx{r}=find(Bonsai_Event==Quit_Rx_code(r));
    reject_idx{r}=find(Bonsai_Event==Reject_Rx_code(r));
    enter_idx{r}=find(Bonsai_Event==Enter_Rx_code(r));
end

figure(1);clf
for k=2:length(RR_offer_Event) % go through all offer events
    r=RR.offer_r_num(k); % restaurant
    j=RR.offer_tone_num(k); % offer tone 
    if k<length(RR_offer_Event)
        offerk_event_idx=RR_offer_idx(k):RR_offer_idx(k+1)-1; % go through following events till next offer tone 
    else
%         offerk_event_idx=RR_offer_idx(k):servo_closed_idx{r}(find(servo_closed_idx{r}>RR_offer_idx(k),1,'first'))+1;
        offerk_event_idx=RR_offer_idx(k):length(Bonsai_Event);
    end
    offerk_event_timestamp=Bonsai_Event_timestamp(offerk_event_idx);
    
    % for non-rejection trial events before enter restaurant
    offerk_event_idx2=RR_offer_idx(k):enter_idx{r}(find(enter_idx{r}>RR_offer_idx(k),1,'first'));
    
    % Outcome 1: Reward Taken
    if sum(ismember(Bonsai_Event(offerk_event_idx),RR_reward_taken_code(r)))
        reward_taken(r,j)=reward_taken(r,j)+1;
        RR.offer_outcome(k)=1;
        RR.reward_taken_timestamp(k)=Bonsai_Event_timestamp(offerk_event_idx(ismember(Bonsai_Event(offerk_event_idx),RR_reward_taken_code(r))));
        RR.servo_open_timestamp(k)=Bonsai_Event_timestamp(offerk_event_idx(ismember(Bonsai_Event(offerk_event_idx),Servo_opened_code(r))));
        RR.accept_timestamp(k)=Bonsai_Event_timestamp(offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),Enter_Rx_code(r)),1,'first')));
        sharp_exit_post_reward_taken_idx=offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),sharp_exit_code(r))&Bonsai_Event_timestamp(offerk_event_idx)>RR.reward_taken_timestamp(k),1,'first'));
        if ~isempty(sharp_exit_post_reward_taken_idx)
            RR.sharp_exit_timestamp(k)=Bonsai_Event_timestamp(sharp_exit_post_reward_taken_idx);
        end
        
    % Outcome 2: Reward Available, but not taken
    elseif sum(ismember(Bonsai_Event(offerk_event_idx),Servo_opened_code(r)))
        reward_avaiable(r,j)=reward_avaiable(r,j)+1;
        RR.offer_outcome(k)=2;
        RR.servo_open_timestamp(k)=Bonsai_Event_timestamp(offerk_event_idx(ismember(Bonsai_Event(offerk_event_idx),Servo_opened_code(r))));
        RR.accept_timestamp(k)=Bonsai_Event_timestamp(offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),Enter_Rx_code(r)),1,'first')));
        sharp_exit_post_reward_taken_idx=offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),sharp_exit_code(r))&Bonsai_Event_timestamp(offerk_event_idx)>RR.servo_open_timestamp(k),1,'first'));
        if ~isempty(sharp_exit_post_reward_taken_idx)
            RR.sharp_exit_timestamp(k)=Bonsai_Event_timestamp(sharp_exit_post_reward_taken_idx);
        end
    
    % Outcome 3: Accept, reward ommitted
    elseif sum(ismember(Bonsai_Event(offerk_event_idx),RR_Rwd_omission_code(r)))
        reward_omission(r,j)=reward_omission(r,j)+1;
        RR.offer_outcome(k)=3;
        RR.accept_timestamp(k)=Bonsai_Event_timestamp(offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),Enter_Rx_code(r)),1,'first')));
        RR.NoRwd_sound_timestamp(k)=Bonsai_Event_timestamp(offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),NoRwd_sound_code(r)),1,'first')));
        sharp_exit_post_reward_taken_idx=offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),sharp_exit_code(r))&Bonsai_Event_timestamp(offerk_event_idx)>RR.NoRwd_sound_timestamp(k),1,'first'));
        if ~isempty(sharp_exit_post_reward_taken_idx)
            RR.sharp_exit_timestamp(k)=Bonsai_Event_timestamp(sharp_exit_post_reward_taken_idx);
        end
        
    % Outcome 4: Quit  
    elseif sum(ismember(Bonsai_Event(offerk_event_idx),Enter_Rx_code(r)))
        quit(r,j)=quit(r,j)+1;
        RR.offer_outcome(k)=4;
        RR.accept_timestamp(k)=Bonsai_Event_timestamp(offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),Enter_Rx_code(r)),1,'first')));
        RR.quit_timestamp(k)=Bonsai_Event_timestamp(offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),Quit_Rx_code(r)),1,'first')));
%         RR.sharp_accept_timestamp=RR.offer_timestamp.*NaN;
        sharp_exit_post_reward_taken_idx=offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),sharp_exit_code(r)),1,'first'));
        if ~isempty(sharp_exit_post_reward_taken_idx)
            RR.sharp_exit_timestamp(k)=Bonsai_Event_timestamp(sharp_exit_post_reward_taken_idx);
        end
        
    % Outcome 5: Reject    
    elseif sum(ismember(Bonsai_Event(offerk_event_idx),Reject_Rx_code(r)))
        reject(r,j)=reject(r,j)+1;
        RR.offer_outcome(k)=5;
        % for rejection trial events before exiting offer zone
        offerk_event_idx2=RR_offer_idx(k):reject_idx{r}(find(reject_idx{r}>RR_offer_idx(k),1,'first'));
        RR.reject_timestamp(k)=Bonsai_Event_timestamp(offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),Reject_Rx_code(r)),1,'first')));
        if RR.reject_timestamp(k)<RR.sharp_exit_timestamp(k)
            RR.offer_dont_use(k)=1;
        end
        sharp_exit_post_reward_taken_idx=offerk_event_idx(find(ismember(Bonsai_Event(offerk_event_idx),sharp_exit_code(r)),1,'first'));
        if ~isempty(sharp_exit_post_reward_taken_idx)
            RR.sharp_exit_timestamp(k)=Bonsai_Event_timestamp(sharp_exit_post_reward_taken_idx);
        end
    end
    first_offerk_entry_idx=offerk_event_idx2(find(ismember(Bonsai_Event(offerk_event_idx2),TJ_entry_code(r)),1,'first'));
    if ~isempty(first_offerk_entry_idx)
        RR.TJ_entry_timestamp(k)=Bonsai_Event_timestamp(first_offerk_entry_idx);
    end    
    
end
subplot_list={1:3,4:6,8:10,11:13};
ylabel_str={'trials','','trials',''};
for r=1:r_num
    h=subplot(2,7,subplot_list{r});hold on;
    for j=1:tone_num
        %Create Bar Graphs
        bar(j,reward_avaiable(r,j)+reward_taken(r,j)+reward_omission(r,j)+quit(r,j)+reject(r,j),'r');
        bar(j,reward_avaiable(r,j)+reward_taken(r,j)+reward_omission(r,j)+quit(r,j),'g');
        bar(j,reward_avaiable(r,j)+reward_taken(r,j)+reward_omission(r,j),'y');
        bar(j,reward_avaiable(r,j)+reward_taken(r,j),'c');
        bar(j,reward_taken(r,j),'b');
    end
    
    %Plot Labels
    set(h,'xtick',[1 2 3 4],'XTickLabel',{'0' '0.2' '0.8' '1'});
    xlabel('offer tone');
    ylabel(ylabel_str{r});
    title(['R-' num2str(r) ', ' num2str(sum(reward_taken(r,:))) ' pellets']);
end
% More Plot Labels
legend({'Rejection','Quit','Accept,NoRwd','Rwd not taken','Reward Taken'});
title(['R-' num2str(r) ', ' num2str(sum(reward_taken(r,:))) ' pellets, total=' num2str(sum(reward_taken(:)))]);

% save data 
fname = append(csv(1:31),'_behaviour_summary.csv');
behaviour_summary = [RR.offer_timestamp, RR.offer_r_num, RR.offer_tone_num, RR.offer_outcome, RR.reject_timestamp];
csvwrite(fname, behaviour_summary)
print = 'done'

end