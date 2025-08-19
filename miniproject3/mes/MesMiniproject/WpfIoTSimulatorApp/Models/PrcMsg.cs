namespace WpfIoTSimulatorApp.Models
{
    // json 전송용 객체. 딴데 안써요
    public class PrcMsg
    {
        public string ClientId { get; set; }
        public string PlantCode { get; set; }
        public string FacilityId { get; set; }
        public string TimeStamp { get; set; }
        public string Flag { get; set; }
    }
}
