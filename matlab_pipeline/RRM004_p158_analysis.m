thisfile=mfilename;
fn=which(mfilename);
addpath([fn(1:find(fn==filesep,2,'last')) 'RR_Behavior_Data' filesep 'RRM004']);
addpath([fn(1:find(fn==filesep,2,'last')) 'RR_FP_Data' filesep 'RRM004']);
time_window=[-2000:25:2500]; % msec
bg_fill_color={[.7 .7 .7],[.7 .7 .7],[.7 .7 .7],[.7 .7 .7]}; % for 415nm trace
fg_fill_color={[0 1 1],[0 1 0],[1 1 0],[1 0 0]}; % for 470nm trace
bg_fill_color={[.5 .7 .7],[.5 .7 .5],[.7 .7 .5],[.7 .4 .5]};
rr_csv = 'RR_FP_Dayp158_epoch-5_ID-RRM004_2021-04-26T14_59_16.csv';
[Bonsai_Event_text, RR]=rr_behaviour_stat(rr_csv);

fp_csv = 'FP_Dayp158_epoch-5_ID-RRM004_2021-04-26T14_59_40.csv';
fpts_csv = 'FPTS_Dayp158_epoch-5_ID-RRM004_2021-04-26T14_59_16.csv';

% read FP file
% FrameCounter,Timestamp,Flags,Region0R,Region1R,Region2G,Region3G
FP = csvread(fp_csv,1,0);
FPTS = csvread(fpts_csv);
FP=FP(3:end,:);
FPTS=FPTS(3:end,:);
fig=figure(1);
set(fig,'Name',[thisfile '_1'],'filename',[thisfile '_1.fig']);
%%
figure(2);clf;
subplot(2,1,1);hold on;
%470 signal (cyan)
flag_470=6;
FP_470_signal=FP(FP(:,3)==flag_470,4:7);
FP_470_time=FPTS(FP(:,3)==flag_470);
plot(FP_470_time,FP_470_signal(:,1:2),'r-');
plot(FP_470_time,FP_470_signal(:,3:4),'g-');
FP_470_signal_baseline=nan(size(FP_470_signal));
FP_470_signal_dff=nan(size(FP_470_signal));
for c=1:size(FP_470_signal,2)
    FP_470_signal_fit = fit(FP_470_time,FP_470_signal(:,c),'exp2');
    FP_470_signal_baseline(:,c)= FP_470_signal_fit(FP_470_time);
    FP_470_signal_dff(:,c)=(FP_470_signal(:,c)-FP_470_signal_baseline(:,c))*1000./FP_470_signal_baseline(:,c);
end
plot(FP_470_time,FP_470_signal_baseline,'k-');
th=text(FP_470_time(round(length(FP_470_time)*.7)),FP_470_signal_baseline(round(length(FP_470_time)*.7)),'470 nm exp2 baseline');
set(th,'color',[0 0 0]);

%415 signal (magenta)
flag_415=1;
FP_415_signal=FP(FP(:,3)==flag_415,4:7);
FP_415_time=FPTS(FP(:,3)==flag_415);
plot(FP_415_time,FP_415_signal(:,1:2),'m-');hold on;
plot(FP_415_time,FP_415_signal(:,3:4),'y-');hold on;
FP_415_signal_baseline=nan(size(FP_415_signal));
FP_415_signal_dff=nan(size(FP_415_signal));
for c=1:size(FP_415_signal,2)
    FP_415_signal_fit = fit(FP_415_time,FP_415_signal(:,c),'exp2');
    FP_415_signal_baseline(:,c)= FP_415_signal_fit(FP_415_time);
    FP_415_signal_dff(:,c)=(FP_415_signal(:,c)-FP_415_signal_baseline(:,c))*1000./FP_415_signal_baseline(:,c);
end
plot(FP_415_time,FP_415_signal_baseline,'k-');
th=text(FP_415_time(round(length(FP_415_time)*.7)),FP_415_signal_baseline(round(length(FP_415_time)*.7)),'415 nm exp2 baseline');
set(th,'color',[0 0 0]);
ylabel('FP ROI intensity');
xlabel('time (mSec)');

%plot df/f * 1000 in green
subplot(2,1,2);hold on;
plot(FP_470_time,FP_470_signal_dff(:,1:2),'r-');
plot(FP_470_time,FP_470_signal_dff(:,3:4),'g-');
th=text(FP_470_time(round(length(FP_470_time)*.7)),FP_470_signal_dff(round(length(FP_470_time)*.7)),'470 nm df/f * 1000');
set(th,'color',[0 0 0]);

ax=axis;
for j=1:4
    for r=1:4
        offer_rj_idx=RR.offer_r_num==r & RR.offer_tone_num==j;
        plot([RR.servo_open_timestamp(offer_rj_idx) RR.servo_open_timestamp(offer_rj_idx)],[ax(3) ax(3)+r],'c');
        plot([RR.reward_taken_timestamp(offer_rj_idx) RR.reward_taken_timestamp(offer_rj_idx)],[ax(3) ax(3)+r],'b');
        plot([RR.TJ_entry_timestamp(offer_rj_idx) RR.TJ_entry_timestamp(offer_rj_idx)],[ax(3) ax(3)+r],'k');
        plot([RR.sharp_exit_timestamp(offer_rj_idx) RR.sharp_exit_timestamp(offer_rj_idx)],[ax(3) ax(3)+r],'r');
        plot([RR.accept_timestamp(offer_rj_idx) RR.accept_timestamp(offer_rj_idx)],[ax(3) ax(3)+r],'y');
        plot([RR.quit_timestamp(offer_rj_idx) RR.quit_timestamp(offer_rj_idx)],[ax(3) ax(3)+r],'g');
        plot([RR.offer_timestamp(offer_rj_idx) RR.offer_timestamp(offer_rj_idx)],[ax(3) ax(3)+r],'k:');
        plot([RR.NoRwd_sound_timestamp(offer_rj_idx) RR.NoRwd_sound_timestamp(offer_rj_idx)],[ax(3) ax(3)+r],'m');
    end
    offer_j_idx=RR.offer_tone_num==j;
    nanmean(RR.servo_open_timestamp(offer_j_idx)-RR.accept_timestamp(offer_j_idx))/1000
end
%%
rejected_offer_idx=find(ismember(RR.offer_outcome,5));
rejected_offer_sharp_exit_then_reject=(RR.reject_timestamp(rejected_offer_idx)-RR.sharp_exit_timestamp(rejected_offer_idx))>0;
RR.reject_timestamp2=RR.reject_timestamp;
RR.reject_timestamp2(rejected_offer_idx(rejected_offer_sharp_exit_then_reject))=RR.sharp_exit_timestamp(rejected_offer_idx(rejected_offer_sharp_exit_then_reject));
for fignum=3:6
    fig=figure(fignum);clf
    set(fig,'Name',[thisfile '_' num2str(fignum)],'filename',[thisfile '_' num2str(fignum)  '.fig']);
    if fignum==3
        figax=[time_window(1) time_window(end) -0.5 0.3];
    elseif fignum==4
        figax=[time_window(1) time_window(end) -0.5 0.3];
    elseif fignum==5
        figax=[time_window(1) time_window(end) -0.8 0.8];
    elseif fignum==6
        figax=[time_window(1) time_window(end) -.45 .3];
    end
    for s=1:8 %go through each restaurant
        if fignum==3 && s==1
            previou_offer_idx=ismember(RR.offer_outcome,[1]); %reward taken,reward omission
            current_offer_idx=ismember(RR.offer_outcome,[1])&(1:length(RR.offer_outcome))'<=length(RR.offer_outcome)*1;
            plot_str1='all restraunt';
            plot_str2='all offer';
            plot_str3='Outcome:Reward (taken)';
            FP470roi=3;
            Hemi_str='Left hemi,green';
            plot_control=1;
        elseif fignum==3 &&s==2
            previou_offer_idx=ismember(RR.offer_outcome,[1]); %reward taken,reward omission
            current_offer_idx=ismember(RR.offer_outcome,[1])&(1:length(RR.offer_outcome))'<=length(RR.offer_outcome)*1;
            plot_str1='all restraunt';
            plot_str2='all offer';
            plot_str3='Outcome:Reward (taken)';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==3 &&s==3
            previou_offer_idx=ismember(RR.offer_outcome,[3]); %reward taken,reward omission
            current_offer_idx=ismember(RR.offer_outcome,[3])&(1:length(RR.offer_outcome))'<=length(RR.offer_outcome)*1;
            plot_str1='all restraunt';
            plot_str2='all offer';
            plot_str3='Outcome:NoReward';
            FP470roi=3;
            Hemi_str='Left hemi,green';
        elseif fignum==3 &&s==4
            previou_offer_idx=ismember(RR.offer_outcome,[3]); %reward taken,reward omission
            current_offer_idx=ismember(RR.offer_outcome,[3])&(1:length(RR.offer_outcome))'<=length(RR.offer_outcome)*1;
            plot_str1='all restraunt';
            plot_str2='all offer';
            plot_str3='Outcome:NoReward';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==3 &&s==5
            previou_offer_idx=ismember(RR.offer_outcome,[2,4]); %RwdNotTaken, Quit
            current_offer_idx=ismember(RR.offer_outcome,[2,4]);
            plot_str1='all restraunt';
            plot_str2='all offer';
            plot_str3='Quit(Y), Rwd(B) not taken';
            FP470roi=3;
            Hemi_str='Left hemi,green';
        elseif fignum==3 &&s==6
            previou_offer_idx=ismember(RR.offer_outcome,[2,4]); %RwdNotTaken, Quit
            current_offer_idx=ismember(RR.offer_outcome,[2,4]);
            plot_str1='all restraunt';
            plot_str2='all offer';
            plot_str3='Quit(Y), Rwd(B) not taken';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==3 &&s==7
            previou_offer_idx=ismember(RR.offer_outcome,[5]); % Rejection
            current_offer_idx=ismember(RR.offer_outcome,[5])&(1:length(RR.offer_outcome))'<=length(RR.offer_outcome)*1;
            plot_str1='all restraunt';
            plot_str2='all offer';
            plot_str3='Rejection';
            FP470roi=3;
            Hemi_str='Left hemi,green';
        elseif fignum==3 &&s==8
            previou_offer_idx=ismember(RR.offer_outcome,[5]); % Rejection
            current_offer_idx=ismember(RR.offer_outcome,[5])&(1:length(RR.offer_outcome))'<=length(RR.offer_outcome)*1;
            plot_str1='all restraunt';
            plot_str2='all offer';
            plot_str3='Rejection';
            FP470roi=4;
            Hemi_str='Right hemi,green';

        % figure 4
        elseif fignum==4 && s==1
            previou_offer_idx=ismember(RR.offer_outcome,[1:4]); % prev trial also reward taken
            current_offer_idx=ismember(RR.offer_outcome,[1:4])&(1:length(RR.offer_outcome))'<=length(RR.offer_outcome)*1;
            plot_str1='All right turn choice, all R';
            plot_str2='all offer';
            plot_str3='Reward taken, omitted, or Quit';
            FP470roi=3;
            Hemi_str='Left hemi,green';
            plot_control=1;
        elseif fignum==4 &&s==2
            previou_offer_idx=ismember(RR.offer_outcome,[1:4]); % prev trial also reward taken
            current_offer_idx=ismember(RR.offer_outcome,[1:4])&(1:length(RR.offer_outcome))'<=length(RR.offer_outcome)*1;
            plot_str1='All right turn choice, all R';
            plot_str2='all offer';
            plot_str3='Reward taken, omitted, or Quit';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==4 &&s==3
            previou_offer_idx=ismember(RR.offer_outcome,5); % prev trial also reward taken
            current_offer_idx=ismember(RR.offer_outcome,5)&(1:length(RR.offer_outcome))'<=length(RR.offer_outcome)*1;
            plot_str1='Left turn Reject, all R';
            plot_str2='all offer';
            plot_str3='Rejection';
            FP470roi=3;
            Hemi_str='Left hemi,green';
        elseif fignum==4 &&s==4
            previou_offer_idx=ismember(RR.offer_outcome,5); % prev trial also reward taken
            current_offer_idx=ismember(RR.offer_outcome,5)&(1:length(RR.offer_outcome))'<=length(RR.offer_outcome)*1;
            plot_str1='Left turn Reject, all R';
            plot_str2='all offer';
            plot_str3='Rejection';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==4 && ismember(s,5:8)
            previou_offer_idx=0;

        % figure 5, split by restraunt
        elseif fignum==5 && s==1
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_r_num==1];
            plot_str1=' R1 ';
            plot_str2='all offer';
            plot_str3='All Outcome';
            FP470roi=3;
            Hemi_str='Left hemi,green';
            plot_control=1;
            fg_fill_color={[1 0 0]}; % for 470nm trace
        elseif fignum==5 &&s==2
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_r_num==1];
            plot_str1=' R1 ';
            plot_str2='all offer';
            plot_str3='All Outcome';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==5 &&s==3
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_r_num==2];
            plot_str1=' R2 ';
            plot_str2='all offer';
            plot_str3='All Outcome';
            FP470roi=3;
            Hemi_str='Left hemi,green';
            fg_fill_color={[1 1 0]}; % for 470nm trace
        elseif fignum==5 &&s==4
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_r_num==2];
            plot_str1=' R2 ';
            plot_str2='all offer';
            plot_str3='All Outcome';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==5 &&s==5
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_r_num==3];
            plot_str1=' R3 ';
            plot_str2='all offer';
            plot_str3='All Outcome';
            FP470roi=3;
            Hemi_str='Left hemi,green';
            fg_fill_color={[0 1 0]}; % for 470nm trace
        elseif fignum==5 &&s==6
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_r_num==3];
            plot_str1=' R3 ';
            plot_str2='all offer';
            plot_str3='All Outcome';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==5 &&s==7
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_r_num==4];
            plot_str1=' R4 ';
            plot_str2='all offer';
            plot_str3='All Outcome';
            FP470roi=3;
            Hemi_str='Left hemi,green';
            fg_fill_color={[0 1 1]}; % for 470nm trace
        elseif fignum==5 &&s==8
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_r_num==4];
            plot_str1=' R4 ';
            plot_str2='all offer';
            plot_str3='All Outcome';
            FP470roi=4;
            Hemi_str='Right hemi,green';

        % figure 6, split by offer tone
        elseif fignum==6 && s==1
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_tone_num==1];
            plot_str1='all restraunt';
            plot_str2='0% offer';
            plot_str3='All Outcome';
            FP470roi=3;
            Hemi_str='Left hemi,green';
            plot_control=1;
            fg_fill_color={[1 0 0]}; % for 470nm trace
        elseif fignum==6 &&s==2
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_tone_num==1];
            plot_str1='all restraunt';
            plot_str2='0% offer';
            plot_str3='All Outcome';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==6 &&s==3
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_tone_num==2];
            plot_str1='all restraunt';
            plot_str2='20% offer';
            plot_str3='All Outcome';
            FP470roi=3;
            Hemi_str='Left hemi,green';
            fg_fill_color={[1 1 0]}; % for 470nm trace
        elseif fignum==6 &&s==4
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_tone_num==2];
            plot_str1='all restraunt';
            plot_str2='20% offer';
            plot_str3='All Outcome';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==6 &&s==5
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_tone_num==3];
            plot_str1='all restraunt';
            plot_str2='80% offer';
            plot_str3='All Outcome';
            FP470roi=3;
            Hemi_str='Left hemi,green';
            fg_fill_color={[0 1 0]}; % for 470nm trace
        elseif fignum==6 &&s==6
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_tone_num==3];
            plot_str1='all restraunt';
            plot_str2='80% offer';
            plot_str3='All Outcome';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        elseif fignum==6 &&s==7
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_tone_num==4];
            plot_str1='all restraunt';
            plot_str2='100% offer';
            plot_str3='All Outcome';
            FP470roi=3;
            Hemi_str='Left hemi,green';
            fg_fill_color={[0 1 1]}; % for 470nm trace
        elseif fignum==6 &&s==8
            previou_offer_idx=repmat(ismember(RR.offer_outcome,[1:5]),1,1);
            current_offer_idx=[RR.offer_tone_num==4];
            plot_str1='all restraunt';
            plot_str2='100% offer';
            plot_str3='All Outcome';
            FP470roi=4;
            Hemi_str='Right hemi,green';
        end
        subplot_shift=(s-1)*3;
        for r=1:size(previou_offer_idx,2)
            plot_offer_idx=find(previou_offer_idx(:,r) & current_offer_idx(:,r)); %find rewarded Left (correct) choice previously also went left
            if isempty(plot_offer_idx)
                subplot(4,6,1+subplot_shift);hold on;
                set(gca,'UserData',[get(gca,'UserData') 0]);
                title([Hemi_str ', ' plot_str1 ', ' plot_str2  sprintf('\n') 'Offer tone, ' num2str(get(gca,'UserData')) ' trials']);
                subplot(4,6,2+subplot_shift);hold on;
                set(gca,'UserData',[get(gca,'UserData') 0]);
                title(['T-Junction entry, ' num2str(get(gca,'UserData')) ' trials']);
                subplot(4,6,3+subplot_shift);hold on;
                set(gca,'UserData',[get(gca,'UserData') 0]);
                title([plot_str3 sprintf('\n')  num2str(get(gca,'UserData')) ' trials']);
            elseif ~isempty(plot_offer_idx)
                subplot(4,6,1+subplot_shift);hold on;
                resampled_FP_470_signal_dff_segmmtI=[];
                resampled_FP_415_signal_dff_segmmtI=[];
                reply='';
                plot_each_trace=0;
                for n=1:length(plot_offer_idx)
                    aligned_event_time=RR.TJ_entry_timestamp(plot_offer_idx(n));
                    % find OfferTone_time before T-entry
                    offer_tone_time_window=RR.offer_timestamp(RR.offer_timestamp>(aligned_event_time+time_window(1)) & RR.offer_timestamp<(aligned_event_time));
                    if  ~isempty(offer_tone_time_window)
                        aligned_event_time=offer_tone_time_window(end);
                        if size(previou_offer_idx,2)==1
                            plot(RR.offer_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'g.');
                            plot(RR.TJ_entry_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'k.');
                            plot(RR.servo_open_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'b.');
                            plot(RR.NoRwd_sound_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'c.');
                            plot(RR.quit_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'y.');
                            if RR.sharp_exit_timestamp(plot_offer_idx(n))~=aligned_event_time
                                h=plot(RR.sharp_exit_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'m.');
                                set(h,'color',[1 .4 1]);
                            end
                            plot(RR.reject_timestamp2(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'r.');
                            if plot_offer_idx(n)>1
                                plot(RR.servo_open_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'b.');
                                plot(RR.NoRwd_sound_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'c.');
                                plot(RR.quit_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'y.');
                                if RR.sharp_exit_timestamp(plot_offer_idx(n)-1)~=RR.reject_timestamp2(plot_offer_idx(n)-1)
                                    h=plot(RR.sharp_exit_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'m.');
                                    set(h,'color',[1 .4 1]);
                                end
                                plot(RR.reject_timestamp2(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'r.');
                            end
                            if plot_offer_idx(n)<length(RR.offer_outcome)
                                plot(RR.offer_timestamp(plot_offer_idx(n)+1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'g.');
                            end
                        end
                        FP_470_segmntI=find(FP_470_time>(aligned_event_time+time_window(1)-50) & FP_470_time<(aligned_event_time+time_window(end)+50));
                        FP_415_segmntI=find(FP_415_time>(aligned_event_time+time_window(1)-50) & FP_415_time<(aligned_event_time+time_window(end)+50));
                        if ~isempty(FP_470_segmntI) %&& length(FP_470_segmntI)*frame_duration/diff(time_window([1 end]))>0.425
                            resampled_FP_470_signal_dff_segmmtI=[resampled_FP_470_signal_dff_segmmtI; interp1(FP_470_time(FP_470_segmntI)-aligned_event_time,FP_470_signal_dff(FP_470_segmntI,FP470roi),time_window,'linear','extrap')];
                            resampled_FP_415_signal_dff_segmmtI=[resampled_FP_415_signal_dff_segmmtI; interp1(FP_415_time(FP_415_segmntI)-aligned_event_time,FP_415_signal_dff(FP_415_segmntI,FP470roi),time_window,'linear','extrap')];
                        else
                            %                 disp(['dropped ' num2str(round((1-length(FP_470_segmntI)*frame_duration/diff(time_window([1 end]))*2)*1000)/10) '% frame in subplot ' num2str(3+subplot_shift) ' trace ' num2str(i)]);
                        end
                    end
                end
                plot([0 0],[figax(3) figax(4)],'k:');
                if plot_control==1
                    FP_Y1=mean(resampled_FP_415_signal_dff_segmmtI,1)+std(resampled_FP_415_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_415_signal_dff_segmmtI(:,1:20),1));
                    FP_Y2=mean(resampled_FP_415_signal_dff_segmmtI,1)-std(resampled_FP_415_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_415_signal_dff_segmmtI(:,1:20),1));
                    h=fill( [time_window fliplr(time_window)],  [FP_Y1 fliplr(FP_Y2)], bg_fill_color{r});hold on;
                    set(h,'EdgeColor','none');
                end
                FP_Y1=mean(resampled_FP_470_signal_dff_segmmtI,1)+std(resampled_FP_470_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_470_signal_dff_segmmtI(:,1:20),1));
                FP_Y2=mean(resampled_FP_470_signal_dff_segmmtI,1)-std(resampled_FP_470_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_470_signal_dff_segmmtI(:,1:20),1));
                h=fill( [time_window fliplr(time_window)],  [FP_Y1 fliplr(FP_Y2)], fg_fill_color{r});hold on;
                set(h,'EdgeColor','none');
                plot(time_window,(mean(resampled_FP_470_signal_dff_segmmtI,1)-mean(mean(resampled_FP_470_signal_dff_segmmtI(:,1:20),1))),'b-');
                axis(figax);
                % set trial number data
                set(gca,'UserData',[get(gca,'UserData') size(resampled_FP_470_signal_dff_segmmtI,1)]);
                title([Hemi_str ', ' plot_str1 ', ' plot_str2  sprintf('\n') 'Offer tone, ' num2str(get(gca,'UserData')) ' trials']);
                xlabel('mSec');
                ylabel('FP signal (a.u.)');

                subplot(4,6,2+subplot_shift);hold on;
                resampled_FP_470_signal_dff_segmmtI=[];
                resampled_FP_415_signal_dff_segmmtI=[];
                reply='';
                plot_each_trace=0;
                for n=1:length(plot_offer_idx)
                    aligned_event_time=RR.TJ_entry_timestamp(plot_offer_idx(n));
                    if size(previou_offer_idx,2)==1
                        plot(RR.offer_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'g.');
                        plot(RR.TJ_entry_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'k.');
                        plot(RR.servo_open_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'b.');
                        plot(RR.NoRwd_sound_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'c.');
                        plot(RR.quit_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'y.');
                        if RR.sharp_exit_timestamp(plot_offer_idx(n))~=aligned_event_time
                            h=plot(RR.sharp_exit_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'m.');
                            set(h,'color',[1 .4 1]);
                        end
                        plot(RR.reject_timestamp2(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'r.');
                        if plot_offer_idx(n)>1
                            plot(RR.servo_open_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'b.');
                            plot(RR.NoRwd_sound_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'c.');
                            plot(RR.quit_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'y.');
                            if RR.sharp_exit_timestamp(plot_offer_idx(n)-1)~=RR.reject_timestamp2(plot_offer_idx(n)-1)
                                h=plot(RR.sharp_exit_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'m.');
                                set(h,'color',[1 .4 1]);
                            end
                            plot(RR.reject_timestamp2(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'r.');
                        end
                        if plot_offer_idx(n)<length(RR.offer_outcome)
                            plot(RR.offer_timestamp(plot_offer_idx(n)+1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'g.');
                        end
                    end
                    FP_470_segmntI=find(FP_470_time>(aligned_event_time+time_window(1)-50) & FP_470_time<(aligned_event_time+time_window(end)+50));
                    FP_415_segmntI=find(FP_415_time>(aligned_event_time+time_window(1)-50) & FP_415_time<(aligned_event_time+time_window(end)+50));
                    if ~isempty(FP_470_segmntI) %&& length(FP_470_segmntI)*frame_duration/diff(time_window([1 end]))>0.425
                        resampled_FP_470_signal_dff_segmmtI=[resampled_FP_470_signal_dff_segmmtI; interp1(FP_470_time(FP_470_segmntI)-aligned_event_time,FP_470_signal_dff(FP_470_segmntI,FP470roi),time_window,'linear','extrap')];
                        resampled_FP_415_signal_dff_segmmtI=[resampled_FP_415_signal_dff_segmmtI; interp1(FP_415_time(FP_415_segmntI)-aligned_event_time,FP_415_signal_dff(FP_415_segmntI,FP470roi),time_window,'linear','extrap')];
                    else
                        %                 disp(['dropped ' num2str(round((1-length(FP_470_segmntI)*frame_duration/diff(time_window([1 end]))*2)*1000)/10) '% frame in subplot ' num2str(3+subplot_shift) ' trace ' num2str(i)]);
                    end
                end
                plot([0 0],[figax(3) figax(4)],'k:');
                if plot_control==1
                    FP_Y1=mean(resampled_FP_415_signal_dff_segmmtI,1)+std(resampled_FP_415_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_415_signal_dff_segmmtI(:,1:20),1));
                    FP_Y2=mean(resampled_FP_415_signal_dff_segmmtI,1)-std(resampled_FP_415_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_415_signal_dff_segmmtI(:,1:20),1));
                    h=fill( [time_window fliplr(time_window)],  [FP_Y1 fliplr(FP_Y2)], bg_fill_color{r});hold on;
                    set(h,'EdgeColor','none');
                end
                FP_Y1=mean(resampled_FP_470_signal_dff_segmmtI,1)+std(resampled_FP_470_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_470_signal_dff_segmmtI(:,1:20),1));
                FP_Y2=mean(resampled_FP_470_signal_dff_segmmtI,1)-std(resampled_FP_470_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_470_signal_dff_segmmtI(:,1:20),1));
                h=fill( [time_window fliplr(time_window)],  [FP_Y1 fliplr(FP_Y2)], fg_fill_color{r});hold on;
                set(h,'EdgeColor','none');
                plot(time_window,(mean(resampled_FP_470_signal_dff_segmmtI,1)-mean(mean(resampled_FP_470_signal_dff_segmmtI(:,1:20),1))),'b-');
                axis(figax);
                % set trial number data
                set(gca,'UserData',[get(gca,'UserData') size(resampled_FP_470_signal_dff_segmmtI,1)]);
                title(['T-Junction entry, ' num2str(get(gca,'UserData')) ' trials']);
                xlabel('mSec');
                ylabel('FP signal (a.u.)');

                subplot(4,6,3+subplot_shift);hold on;
                resampled_FP_470_signal_dff_segmmtI=[];
                resampled_FP_415_signal_dff_segmmtI=[];
                reply='';
                plot_each_trace=0;
                for n=1:length(plot_offer_idx)
                    aligned_event_time=nansum([RR.servo_open_timestamp(plot_offer_idx(n)) RR.NoRwd_sound_timestamp(plot_offer_idx(n)) RR.reject_timestamp2(plot_offer_idx(n)) RR.quit_timestamp(plot_offer_idx(n))]);
                    if size(previou_offer_idx,2)==1 %only plot detailed event with one trace
                        plot(RR.offer_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'g.');
                        plot(RR.TJ_entry_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'k.');
                        plot(RR.servo_open_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'b.');
                        plot(RR.NoRwd_sound_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'c.');
                        plot(RR.quit_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'y.');
                        if RR.sharp_exit_timestamp(plot_offer_idx(n))~=aligned_event_time
                            h=plot(RR.sharp_exit_timestamp(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'m.');
                            set(h,'color',[1 .4 1]);
                        end
                        plot(RR.reject_timestamp2(plot_offer_idx(n))-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'r.');
                        if plot_offer_idx(n)>1
                            plot(RR.servo_open_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'b.');
                            plot(RR.NoRwd_sound_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'c.');
                            plot(RR.quit_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'y.');
                            if RR.sharp_exit_timestamp(plot_offer_idx(n)-1)~=RR.reject_timestamp2(plot_offer_idx(n)-1)
                                h=plot(RR.sharp_exit_timestamp(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'m.');
                                set(h,'color',[1 .4 1]);
                            end
                            plot(RR.reject_timestamp2(plot_offer_idx(n)-1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'r.');
                        end
                        if plot_offer_idx(n)<length(RR.offer_outcome)
                            plot(RR.offer_timestamp(plot_offer_idx(n)+1)-aligned_event_time,n*0.8*figax(3)/length(plot_offer_idx)+0.2*figax(3),'g.');
                        end
                    end
                    FP_470_segmntI=find(FP_470_time>(aligned_event_time+time_window(1)-50) & FP_470_time<(aligned_event_time+time_window(end)+50));
                    FP_415_segmntI=find(FP_415_time>(aligned_event_time+time_window(1)-50) & FP_415_time<(aligned_event_time+time_window(end)+50));
                    if ~isempty(FP_470_segmntI) %&& length(FP_470_segmntI)*frame_duration/diff(time_window([1 end]))>0.425
                        resampled_FP_470_signal_dff_segmmtI=[resampled_FP_470_signal_dff_segmmtI; interp1(FP_470_time(FP_470_segmntI)-aligned_event_time,FP_470_signal_dff(FP_470_segmntI,FP470roi),time_window,'linear','extrap')];
                        resampled_FP_415_signal_dff_segmmtI=[resampled_FP_415_signal_dff_segmmtI; interp1(FP_415_time(FP_415_segmntI)-aligned_event_time,FP_415_signal_dff(FP_415_segmntI,FP470roi),time_window,'linear','extrap')];
                    else
                        %                 disp(['dropped ' num2str(round((1-length(FP_470_segmntI)*frame_duration/diff(time_window([1 end]))*2)*1000)/10) '% frame in subplot ' num2str(3+subplot_shift) ' trace ' num2str(i)]);
                    end
                end
                plot([0 0],[figax(3) figax(4)],'k:');
                if plot_control==1
                    FP_Y1=mean(resampled_FP_415_signal_dff_segmmtI,1)+std(resampled_FP_415_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_415_signal_dff_segmmtI(:,1:20),1));
                    FP_Y2=mean(resampled_FP_415_signal_dff_segmmtI,1)-std(resampled_FP_415_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_415_signal_dff_segmmtI(:,1:20),1));
                    h=fill( [time_window fliplr(time_window)],  [FP_Y1 fliplr(FP_Y2)], bg_fill_color{r});hold on;
                    set(h,'EdgeColor','none');
                end
                FP_Y1=mean(resampled_FP_470_signal_dff_segmmtI,1)+std(resampled_FP_470_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_470_signal_dff_segmmtI(:,1:20),1));
                FP_Y2=mean(resampled_FP_470_signal_dff_segmmtI,1)-std(resampled_FP_470_signal_dff_segmmtI,1)./sqrt(length(plot_offer_idx)-1)-mean(mean(resampled_FP_470_signal_dff_segmmtI(:,1:20),1));
                h=fill( [time_window fliplr(time_window)],  [FP_Y1 fliplr(FP_Y2)], fg_fill_color{r});hold on;
                set(h,'EdgeColor','none');
                plot(time_window,(mean(resampled_FP_470_signal_dff_segmmtI,1)-mean(mean(resampled_FP_470_signal_dff_segmmtI(:,1:20),1))),'b-');
                axis(figax);
                % set trial number data
                set(gca,'UserData',[get(gca,'UserData') size(resampled_FP_470_signal_dff_segmmtI,1)]);
                title([plot_str3 sprintf('\n')  num2str(get(gca,'UserData')) ' trials']);
                xlabel('mSec');
                ylabel('FP signal (a.u.)');
            end
        end
    end
    shg;
end
