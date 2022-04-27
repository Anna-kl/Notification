import json
import smtplib
from datetime import datetime
from functools import reduce

from flask import render_template

html = '''<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="utf-8"> <!-- utf-8 works for most cases -->
  <meta name="viewport" content="width=device-width"> <!-- Forcing initial-scale shouldn't be necessary -->
  <meta http-equiv="X-UA-Compatible" content="IE=edge"> <!-- Use the latest (edge) version of IE rendering engine -->
  <meta name="x-apple-disable-message-reformatting">  <!-- Disable auto-scale in iOS 10 Mail entirely -->
  <meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no"> <!-- Tell iOS not to automatically link certain text strings. -->
  <meta name="color-scheme" content="light">
  <meta name="supported-color-schemes" content="light">
  <title></title> <!--   The title tag shows in email notifications, like Android 4.4. -->
  <xml>
    <o:OfficeDocumentSettings>
      <o:AllowPNG/>
      <o:PixelsPerInch>96</o:PixelsPerInch>
    </o:OfficeDocumentSettings>
  </xml>


</head>
<body width="100%" style="margin: 0; padding: 0 !important; mso-line-height-rule: exactly; background-color: #ffffff;">
<div class="main-container">
    <div class="cards" style="display: flex;
  flex-wrap: wrap;
 align-items: center;
  justify-content: center;">
      <div class="card card-1" style="margin: 20px;
  padding: 20px;
  width: 500px;
  min-height: 200px;
  display: grid;
  grid-template-rows: 20px 50px 1fr 50px;
  border-radius: 10px;
  box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.25);
  transition: all 0.2s;
 background: radial-gradient(#FFE97F, #fff);">
        <div class="heading" style="text-align: center;">
          <h1 class="heading__title" style="font-weight: 600;">Уважаемый руководитель</h1>
          <p class="heading__credits" style="margin: 10px 0px;
  color: #888888;
  font-size: 25px;
  transition: all 0.5s;" > Отчет по insert1 обновлен </p>
          <p class="heading__credits" style="margin: 10px 0px;
  color: #888888;
  font-size: 25px;
  transition: all 0.5s;"><a class="heading__link" target="_blank" href="https://monitoring.gpn.supply">Просмотреть отчет по ссылке</a></p>
        </div>
      </div>
    </div>
    <div class="cards" style="display: flex;
  flex-wrap: wrap;
 align-items: center;
  justify-content: center;">
      <div class="card card-1" style="margin: 20px;
  padding: 20px;
  width: 500px;
  min-height: 200px;
  display: grid;
  grid-template-rows: 20px 50px 1fr 50px;
  border-radius: 10px;
  box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.25);
  transition: all 0.2s;
 background: radial-gradient(#58f, rgb(58, 57, 91));">
        <div class="card__icon" style="grid-row: 2/3;
  font-size: 30px;"><i class="fas fa-bolt"></i></div>
        <p class="card__exit" style="grid-row: 1/2;
  justify-self: end;"><i class="fas fa-times"></i></p>
        <h2 class="card__title" style="grid-row: 3/4;
  font-weight: 400;
  color: #ffffff;">insert0</h2>
        <p class="card__apply" style="grid-row: 4/5;
  align-self: center;">
          <a class="card__link" style="position: relative;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.9);" href="#">Показателей обновлено: insert2<i class="fas fa-arrow-right"></i></a>
        </p>
        <p class="card__apply" style="grid-row: 4/5;
  align-self: center;">
          <a class="card__link" style="position: relative;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.9);" href="#">Локаций: insert3<i class="fas fa-arrow-right"></i></a>
        </p>
      </div>


    </div>
  </div>

</body>
</html>
'''


def sendEmail(email_address, data_insert, startPeriod, endPeriod):
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    mtrTypes = json.load(open('mtrTypes', encoding='utf8'))
    fromaddr = "klimova_88@mail.ru"
    toaddr = email_address
    mypass = "4cqJXh2Gu1GauJMgHYa2"

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Logotech Lab"
    # body = "Текущий отчет"
    # msg.attach(MIMEText(body, 'plain'))
    count = list(map(lambda x: x['count'], data_insert))
    count = reduce(lambda x, y: x + y, count)

    mtr = []
    for item in data_insert:
        mtr.extend(list(filter(lambda x: x['id'] == item['mtrType'], mtrTypes)))
    mtr = set(map(lambda x: x['name'].split(',')[0], mtr))
    mtr = ','.join(mtr)

    if count == 0:
        insert = 'Показатели не были вовремя загружены в систему'
    else:
        insert = 'Показатели были загружены в систему'

    location_s = []
    distinct_locations = []
    list(map(lambda x: location_s.extend(x['locations']), data_insert))
    distinct_locations = [i for i in location_s if i not in distinct_locations]
    part2 = MIMEText(html.replace('insert1', mtr). \
                     replace('insert2', str(count)). \
                     replace('insert0', insert). \
                     replace('insert3', str(len(distinct_locations))), 'html')
    # part2 = MIMEText(html.replace('insert1', startPeriod.strftime('%Y-%m-%d %H:%M'))
    #                  .replace('insert2', endPeriod.strftime('%Y-%m-%d %H:%M'))
    #                  .replace('insert3', datetime.now().strftime('%Y-%m-%d %H:%M'))
    #                  .replace('insert4', str(count))
    #                  .replace('insert5', str(len(distinct_locations)))
    #                  .replace('insert7', '\n'.join(distinct_locations)), 'html')

    msg.attach(part2)

    server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    # server.starttls()
    server.login(fromaddr, mypass)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
