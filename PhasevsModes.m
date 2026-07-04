% Code for graphing detected phase vs mode sent

% Initialize variables
DL = -10:10;
Delta_t = 25;
Phi = DL*Delta_t/2 + 5;
CombinedPD = [];

% Loop for reading and averaging the data collected
for n = 1:4
    Data = load(strcat(num2str(n),'.mat'));
    CombinedPDb = zeros(size(Data.PhaseDiff(:,:,1)));
    for mm = 1:4
        CombinedPDb = CombinedPDb + Amend2(Data.PhaseDiff(:,:,mm));
    end
    CombinedPDb = CombinedPDb / 4;
    CombinedPD = [CombinedPD; CombinedPDb;];
end 

CombinedPD = CombinedPD*209*180/pi; 
STDV = std(CombinedPD);
meanPD = mean(CombinedPD);

% Error bar graph 
figure(3)
errorbar(DL, meanPD, STDV,'o','MarkerFaceColor','auto','LineWidth',1.5)
hold on
plot(DL,Phi,'LineWidth',1)
xticks(DL)
xticklabels({'-10','','','','','-5','','','','','0','','','','','5','','','','','10'})
yticks(-150:25:150)
yticklabels({'-150','','-100','','-50','','0','','50','','100','','150'})
xtickangle(0)
xlim([-10 10])
ylim([-150 150])
grid on;
ax = gca; ax.GridAlpha = 0.25; ax.GridLineStyle = '--'; ax.Layer = 'top';
set(gca,'FontSize',13)
fontsize(gcf,scale=1.4)
hold off
