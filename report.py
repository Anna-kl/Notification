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
        <style>
            * {
                font-family: sans-serif !important;
            }
        </style>

    <style>

        /* What it does: Tells the email client that only light styles are provided but the client can transform them to dark. A duplicate of meta color-scheme meta tag above. */
        :root {
          color-scheme: light;
          supported-color-schemes: light;
        }

        /* What it does: Remove spaces around the email design added by some email clients. */
        /* Beware: It can remove the padding / margin and add a background color to the compose a reply window. */
        html,
        body {
            margin: 0 auto !important;
            padding: 0 !important;
            height: 100% !important;
            width: 100% !important;
        }

        /* What it does: Stops email clients resizing small text. */
        * {
            -ms-text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%;
        }

        /* What it does: Centers email on Android 4.4 */
        div[style*="margin: 16px 0"] {
            margin: 0 !important;
        }

        /* What it does: forces Samsung Android mail clients to use the entire viewport */
        #MessageViewBody, #MessageWebViewDiv{
            width: 100% !important;
        }

        /* What it does: Stops Outlook from adding extra spacing to tables. */
        table,
        td {
            mso-table-lspace: 0pt !important;
            mso-table-rspace: 0pt !important;
        }

        /* What it does: Fixes webkit padding issue. */
        table {
            border-spacing: 0 !important;
            border-collapse: collapse !important;
            table-layout: fixed !important;
            margin: 0 auto !important;
        }

        /* What it does: Uses a better rendering method when resizing images in IE. */
        img {
            -ms-interpolation-mode:bicubic;
        }

        /* What it does: Prevents Windows 10 Mail from underlining links despite inline CSS. Styles for underlined links should be inline. */
        a {
            text-decoration: none;
        }

        /* What it does: A work-around for email clients meddling in triggered links. */
        a[x-apple-data-detectors],  /* iOS */
        .unstyle-auto-detected-links a,
        .aBn {
            border-bottom: 0 !important;
            cursor: default !important;
            color: inherit !important;
            text-decoration: none !important;
            font-size: inherit !important;
            font-family: inherit !important;
            font-weight: inherit !important;
            line-height: inherit !important;
        }

        /* What it does: Prevents Gmail from displaying a download button on large, non-linked images. */
        .a6S {
            display: none !important;
            opacity: 0.01 !important;
        }

        /* What it does: Prevents Gmail from changing the text color in conversation threads. */
        .im {
            color: inherit !important;
        }

        /* If the above doesn't work, add a .g-img class to any image in question. */
        img.g-img + div {
            display: none !important;
        }

        /* What it does: Removes right gutter in Gmail iOS app: https://github.com/TedGoas/Cerberus/issues/89  */
        /* Create one of these media queries for each additional viewport size you'd like to fix */

        /* iPhone 4, 4S, 5, 5S, 5C, and 5SE */
        @media only screen and (min-device-width: 320px) and (max-device-width: 374px) {
            u ~ div .email-container {
                min-width: 320px !important;
            }
        }
        /* iPhone 6, 6S, 7, 8, and X */
        @media only screen and (min-device-width: 375px) and (max-device-width: 413px) {
            u ~ div .email-container {
                min-width: 375px !important;
            }
        }
        /* iPhone 6+, 7+, and 8+ */
        @media only screen and (min-device-width: 414px) {
            u ~ div .email-container {
                min-width: 414px !important;
            }
        }

    </style>


</head>
<body width="100%" style="margin: 0; padding: 0 !important; mso-line-height-rule: exactly; background-color: #ffffff;">
	<center role="article" aria-roledescription="email" lang="en" style="width: 100%; background-color: #ffffff;">
    <!--[if mso | IE]>
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #ffffff;">
    <tr>
    <td>
    <![endif]-->

        <!-- Visually Hidden Preheader Text : BEGIN -->
        <div style="max-height:0; overflow:hidden; mso-hide:all;" aria-hidden="true">
            Текущий отчет готов
        </div>
        <!-- Visually Hidden Preheader Text : END -->

        <!-- Create white space after the desired preview text so email clients don’t pull other distracting text into the inbox preview. Extend as necessary. -->
        <!-- Preview Text Spacing Hack : BEGIN -->
        <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all; font-family: sans-serif;">
	        &zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;&zwnj;&nbsp;
        </div>
        <!-- Preview Text Spacing Hack : END -->

        <!--
            Set the email width. Defined in two places:
            1. max-width for all clients except Desktop Windows Outlook, allowing the email to squish on narrow but never go wider than 600px.
            2. MSO tags for Desktop Windows Outlook enforce a 600px width.
        -->
        <div style="max-width: 600px; margin: 0 auto;" class="email-container">
            <!--[if mso]>
            <table align="center" role="presentation" cellspacing="0" cellpadding="0" border="0" width="600">
            <tr>
            <td>
            <![endif]-->

	        <!-- Email Body : BEGIN -->
	        <table align="center" role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin: auto;">
		        <!-- Email Header : BEGIN -->
	            <tr>
	                <td style="padding: 20px 0; text-align: center">
	             
</td>
	            </tr>

                <tr>
                    <td style="background-color: #ffffff;">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                            <tr>
                            <tr>
                                <td style="padding: 20px; font-family: sans-serif; font-size: 15px; line-height: 20px; color: #555555;">
                                    <h1 style="margin: 0 0 10px 0; font-family: sans-serif; font-size: 25px; line-height: 30px; color: #333333; font-weight: normal;">Показатели загружены в систему</h1>
                                    <p>Здравствуйте, Уважаемый руководитель,
                                    <p> {insert1}</p>
<a href="https://monitoring.gpn.supply/"> просмотреть отчет можно по ссылке </a></p>

                                </td>
                            </tr>

                            
                        </table>
                    </td>
                </tr>
                <!-- 1 Column Text + Button : END -->

                <!-- 2 Even Columns : BEGIN -->
                
  

            </table>


            <!--[if mso]>
            </td>
            </tr>
            </table>
            <![endif]-->
        </div>
    </td>
    </tr>
    </table>
    <![endif]-->
    </center>
</body>
</html>'''

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
    count = reduce(lambda x, y: x+y, count)

    mtr = []
    for item in data_insert:
        mtr.extend(list(filter(lambda x: x['id'] == item['mtrType'], mtrTypes)))
    mtr = list(map(lambda x: x['name'], mtr))
    mtr = ','.join(mtr)

    if count == 0:
        insert = 'Показатели не были вовремя загружены в систему'
    else:
        insert = 'Показатели: {0} - готовы'.format(mtr)

    location_s = []
    distinct_locations=[]
    list(map(lambda x: location_s.extend(x['locations']), data_insert))
    distinct_locations = [i for i in location_s if i not in distinct_locations]
    part2 = MIMEText(html.replace('{insert1}', insert), 'html')
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
