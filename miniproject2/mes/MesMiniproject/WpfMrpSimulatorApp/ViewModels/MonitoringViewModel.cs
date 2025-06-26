using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MahApps.Metro.Controls.Dialogs;
using MySqlConnector;
using System.Data;
using System.Threading.Tasks;
using System.Windows.Media;
using WpfMrpSimulatorApp.Helpers;

namespace WpfMrpSimulatorApp.ViewModels
{
    public partial class MonitoringViewModel : ObservableObject
    {
        // readonly 생성자에서 할당하고나면 그 이후에 값변경 불가
        private readonly IDialogCoordinator dialogCoordinator;
        private Brush _productBrush;
        private string _plantName;
        private string _prcDate;
        private string _prcLoadTime;
        private string _prcFacilityName;
        private int _schAmount;
        private int _successAmount;
        private int _failAmount;
        private string _successRate;
        private int _schIdx;

        public MonitoringViewModel(IDialogCoordinator coordinator)
        {
            this.dialogCoordinator = coordinator;  // 파라미터값으로 초기화

            SchIdx = 1; // 최초 1부터 시작
        }

        public Brush ProductBrush
        {
            get => _productBrush;
            set => SetProperty(ref _productBrush, value);
        }

        public string PlantName
        {
            get => _plantName;
            set => SetProperty(ref _plantName, value);
        }

        public string PrcDate
        {
            get => _prcDate;
            set => SetProperty(ref _prcDate, value);
        }

        public string PrcLoadTime
        {
            get => _prcLoadTime;
            set => SetProperty(ref _prcLoadTime, value);
        }

        public string PrcFacilityName
        {
            get => _prcFacilityName;
            set => SetProperty(ref _prcFacilityName, value);
        }

        public int SchAmount
        {
            get => _schAmount;
            set => SetProperty(ref _schAmount, value);
        }

        public int SuccessAmount
        {
            get => _successAmount;
            set => SetProperty(ref _successAmount, value);
        }
        public int FailAmount
        {
            get => _failAmount;
            set => SetProperty(ref _failAmount, value);
        }

        public string SuccessRate
        {
            get => _successRate;
            set => SetProperty(ref _successRate, value);
        }

        public int SchIdx
        {
            get => _schIdx;
            set => SetProperty(ref _schIdx, value);
        }


        private void SetProperty(ref object prcDate, string value)
        {
            throw new NotImplementedException();
        }

        public event Action? StartHmiRequested;
        public event Action? StartSensorCheckRequested; // VM에서 View에 있는 이벤트를 호출

        public void CheckAni()
        {
            StartSensorCheckRequested?.Invoke(); // 센서 애니메이션 동작 요청

            // 양품불량품 판단
            Random rand = new();
            int result = rand.Next(1, 3); // 1 ~ 2

            ProductBrush = result switch
            {
                1 => Brushes.Green, // 양품
                2 => Brushes.Crimson, // 불량
                _ => Brushes.Aqua,      // default 혹시나
            };
        }

        [RelayCommand]
        public async Task SearchProcess()
        {
            // await this.dialogCoordinator.ShowMessageAsync(this, "공정조회", "조회를 시작합니다");
            try
            {
                string query = @"SELECT sch.schIdx, sch.plantCode, set1.codeName AS plantName,
                                        sch.schDate, sch.loadTime,
                                        sch.schStartTime, sch.schEndTime,
                                        sch.schFacilityId, set2.codeName AS schFacilityName,
                                        sch.schAmount    
                                   FROM schedules AS sch
                                   JOIN settings AS set1
                                     ON sch.plantCode = set1.BasicCode
                                   JOIN settings AS set2
                                     ON sch.schFacilityId = set2.BasicCode
                                  WHERE sch.schIdx = @schIdx";
                DataSet ds = new DataSet();

                using (MySqlConnection conn = new MySqlConnection(Common.CONNSTR))
                {
                    conn.Open();
                    MySqlCommand cmd = new MySqlCommand(query, conn);
                    cmd.Parameters.AddWithValue("@schIdx", SchIdx);
                    MySqlDataAdapter adapter = new MySqlDataAdapter();
                    

                    adapter.Fill(ds, "Result");
                }

                if (ds.Tables["Result"].Rows.Count != 0)
                {
                    DataRow row = ds.Tables["Result"].Rows[0];
                    PlantName = row["plantName"].ToString();
                    PrcDate = Convert.ToDateTime(row["schDate"]).ToString("yyyy-MM-dd");
                    PrcLoadTime = row["loadTime"].ToString();
                    PrcFacilityName = row["schFacilityName"].ToString();
                    SchAmount =  Convert.ToInt32(row["schAmount"]);
                    SchAmount = FailAmount = 0;
                    SuccessRate = "0.0 %";
                }
                else
                {
                    await this.dialogCoordinator.ShowMessageAsync(this, "공정조회", "해당 공정이 없습니다.");
                    PlantName = string.Empty; // 공정내용 전부 초기화
                    PrcDate = string.Empty;
                    PrcLoadTime = string.Empty;
                    PrcFacilityName = string.Empty;
                    SchAmount = 0;
                    SchAmount = FailAmount = 0;
                    SuccessRate= "0.0 %";

                    return;
                }

                

            }
            catch (Exception ex)
            {

                await this.dialogCoordinator.ShowMessageAsync(this, "오류", ex.Message);
            }
           
        }

        [RelayCommand]
        public async Task StartProcess()
        {
            ProductBrush = Brushes.Gray;
            StartHmiRequested?.Invoke();  // 컨베이어벨트 애니메이션 요청(View에서 처리)
        }


    }
}
