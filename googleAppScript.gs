// Global Variables & Configurations

// Google Sheet Location
var str_pay = "B2:G2"
var str_cate = "A4:L4"
var url = 'https://docs.google.com/spreadsheets/d/1_awQkXTsZ-0WvKYKIDP9yvU2aucLbICb768j6PNAXVY/edit?usp=sharing'


var SpreadSheet = SpreadsheetApp.openByUrl(url);
var sheet = SpreadSheet.getActiveSheet();

// Fonts and Colors
var FONT = 'Roboto'
var BACKGROUND_COLOR = ['#ead1dc', '#f4cccc', '#fce5cd', '#fff2cc', '#d9ead3', '#c9daf8', '#d9d2e9' ] // Backgroud color for Sunday -> Saturday
// -------------------------------------

// Date 
function cal_date(){
  var d  = new Date(), y  = new Date();
  y.setDate(y.getDate() - 1); 
  var dates = [String(y.getFullYear() + '/' + (y.getMonth()+1) + '/' + y.getDate())];
  
  Logger.log(dates);
  
  var n = d.getFullYear() + '/' + (d.getMonth()+1) + '/' + d.getDate();
  
  // return array
  //  0            1            2        3         4
  // "yd:YYYY/m/d  td:YYYY/m/d  Yd:m/dd  td:m/dd"  Weekday:[0-6]
  dates.push(String(n));
  // serial number prefix: m/dd
  dates.push((y.getMonth()+1)*100 +y.getDate());
  dates.push((d.getMonth()+1)*100 +d.getDate());
  dates.push(d.getDay())
  
  return dates;
}

// Get Function for get last row information
function doGet(e) {
  // states:1 call for updates (get categories and payment methods)
  // states:2 get last column
  
  var a = sheet.getRange(str_pay).getValues()[0]
  var b = sheet.getRange(str_cate).getValues()[0]
  var j = {"pay": a, "cate": b}
  var end = JSON.stringify(j)
  
  var output = ContentService.createTextOutput(end)
  return output
}

// Post New Record
// e should contains color & data for today
function doPost(e) {
  if(typeof e.parameter.checkWebhook !== 'undefined'){
    return ContentService.createTextOutput("OK")
  }
  
  var para = e.parameter;
  var lastRow = sheet.getLastRow();
  var lastCol = sheet.getLastColumn();
  var lastCel = sheet.getRange(lastRow, lastCol-1);
  var range;
  var error;
  var dates = cal_date();
  
  var lastCel_date, lastCel_serial;
  lastCel_date = (lastCel.getValue() / 100) >> 0; 
  lastCel_serial = lastCel.getValue() % 100;
  
  var cate = para.cate
  var price = -1 * para.price
  var costfrom = para.costfrom
  var log = para.log
  var bgColor = BACKGROUND_COLOR[dates[4]]
                                 
  // next version                              
  //var bgColor = para.bgColor
  //var font = para.font
  
  if(lastCel_date != dates[3] && lastCel_serial != 1){
    sheet.appendRow([dates[1], cate, price, costfrom, log, "","","","","","",dates[3]*100+1,       false]);
    lastCel = sheet.getRange(lastRow+1, lastCol);
    lastCel.insertCheckboxes();
  }else{
    sheet.appendRow(["",       cate, price, costfrom, log, "","","","","","",lastCel.getValue()+1 , ""]);
    lastCel = sheet.getRange(lastRow+1, lastCol);
    lastCel.removeCheckboxes();
  }
  //Logger.log()
  range = sheet.getRange(lastRow+1, 1, 1, lastCol);
  range.setFontFamily(FONT)
  range.setBackground(bgColor)
  
  if(error == 1){
    return ContentService.createTextOutput("NOK")
  }
  return ContentService.createTextOutput("OK")
}

