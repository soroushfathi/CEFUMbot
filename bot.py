import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler, ConversationHandler,
)
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Update,
    ParseMode,
    error,
)
from telegram.ext.filters import Filters
from telegram.chataction import ChatAction
from bs4 import BeautifulSoup
from uuid import uuid4
import requests
from telegram.utils.helpers import escape_markdown

# TODO memari computer
BASE_URL = 'http://ce.um.ac.ir/index.php?lang=fa'
ARTICLES_URL = 'http://ce.um.ac.ir/index.php?option=com_groups&view=enarticles&edugroups=3105&cur_stu_title=&Itemid=694&lang=fa'

messages = {
    'msg_start_private': '🤖سلام {}، \n خوش امدی به ربات🙂; امیدوارم بتونم کمکت کنم🤠',
    'msg_start_group': '🤖سلام بر بچه های گروه {} ;\n خوشحالم که اومدم تو گروهتون🙂;\n امیدوارم بتونم کمکتون کنم🤠',
    'msg_start_supergroup': '🤖سلام بر بچه های گروه {} ;\n خوشحالم که اومدم تو گروهتون🙂;\n امیدوارم بتونم کمکتون کنم🤠',
    'msg_start_channel': 'سلام و وقت بخیر اعضای محترم کانال، \n 🙂، امیدوارم بتونم کمکتون کنم🤠',
    'msg_contact': 'نظرات 👨🏻‍💻 انتقادات 🧑🏻‍🎓 پیشنهادات',
    'msg_main_handler': 'منوی اصلی🗂️:',
    'msg_select_src_subject': 'درس مورد نظر را انتخاب کنید:',
    'msg_select_exe_subject': ' درس مورد نظر را انتخاب کنید:',
    'msg_college': 'گروه مهندسی کامپیوتر🖥 : ',
    'msg_college_press': 'انتشارات مهندسی کامپیوتر فردوسی مشهد: ',
    'msg_send_document': 'ممنون {} 😍 بابت همکاری برای تکمیل ربات🙌🏻 \n '
                         'فایل مورد نظر را ارسال کنید:\n'
                         'نام درس و استاد مربوطه هم در اسم فایل ذکر شود + توضیحات در صورت نیاز',
    'msg_send_document2': 'فایل با موفقیت دریافت شد✅با تشکر🙏🏻',
    'msg_network_error': 'به دلیل سرعت پایین شبکه، ارسال فایل با مشکل مواجه شد😣 \n '
                         'به زودی مشکل را حل خواهیم کرد🤠\n'
                         'با عرض پوزش🙏🏻',
    'msg_sending_time': 'به دلیل سرعت پایین شبکه، ارسال فایل ممکن '
                        'است تا دو دقیقه طول بکشد😣 \n '
                        'به زودی مشکلو حل خواهیم کرد🤠\n'
                        'با تشکر از صبر شما🙏🏻',
    'msg_college_about': 'در سال ۱۳۴۹ هجری خورشیدی همزمان با دانشگاه تهران و دانشگاه صنعتی شریف، '
                         'رشته آمار و ماشین های حسابگر در مقطع کارشناسی در دانشکده علوم دانشگاه فردوسی مشهد تأسیس شد.'
                         ' بعدها این رشته به نام کامپیوتر تغییر نام یافت تا اینکه در سال ۱۳۶۷ گروه مهندسی کامپیوتر'
                         ' در دانشکده مهندسی شکل گرفت و پذیرش دانشجو در مقطع کارشناسی رشته مهندسی کامپیوتر گرایش نرم '
                         'افزار در دانشکده مهندسی آغاز گردید. گروه مهندسی کامپیوتر در سال ۱۳۷۴ پذیرش دانشجو در مقطع'
                         ' کارشناسی ارشد مهندسی کامپیوتر گرایش نرم افزار را آغاز کرد. در سال ۱۳۷۹ گرایش سخت افزار'
                         ' به گرایش های رشته مهندسی کامپیوتر گروه اضافه شد و پذیرش دانشجو در مقطع کارشناسی گرایش '
                         'سخت افزار شروع شد. گروه مهندسی کامپیوتر در سال ۱۳۸۵ پذیرش دانشجو در مقطع دکترای تخصصی '
                         'مهندسی کامپیوتر گرایش نرم افزار را شروع کرد. پذیرش دانشجو در مقاطع کارشناسی ارشد و دکترای'
                         ' تخصصی مهندسی کامپیوتر گرایش هوش مصنوعی به ترتیب در سال های ۱۳۸۷ و ۱۳۹۴ آغاز شد. گروه مهندسی '
                         'کامپیوتر از سال ۱۳۹۳ اقدام به پذیرش دانشجو در مقطع کارشناسی ارشد مهندسی فناوری اطلاعات گرایش '
                         'شبکه های کامپیوتری کرده است. علاوه بر این، گروه مهندسی کامپیوتر از مهرماه ۱۳۹۶ پذیرش دانشجو'
                         ' در مقطع کارشناسی ارشد مهندسی کامپیوتر گرایش معماری کامپیوتر (سخت افزار) را شروع خواهد کرد. ',
    'msg_college_contact': '''☎️تلفن:۰۵۱-۳۸۸۰۶۰۵۹
 📠نمابر: ۰۵۱-۳۸۸۰۷۱۸۱
📭كدپستی: ۹۱۷۷۹۴۸۹۷۴
📧پست الکترونیک: ce.um.ac.ir''',
    'msg_masters_noriBaigi': '👨🏻‍🏫مصطفی نوری بایگی\n'
                             ' ۰۵۱-۳۸۸۰۵۱۷۲ ☎️\n'
                             'nouribaygi@um.ac.ir 📧\n'
                             'تلگرام : @nourii\n'
                             '🗄تحصیلات: \n'
                             '\t🔰مرتبه علمی: استادیار\n'
                             '\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر - نرم افزار\n'
                             '\t🔰محل اخذ آخرین مدرک تحصیلی: دانشگاه صنعتی شریف، تهران، ایران\n'
                             '🏷توضیحات: \n استادی هستن که زیاد سطح بالا تدریس نمیکنن ولی از دانشجو سطح بالا میخواد.\n'
                             'در مجازی تدریس به صورت افلاین و آنلاین انجام میشه\n'
                             '\nنظرات دانشجویان💡 : \n'
                             'https://t.me/Comp_Professors/86\n'
                             'https://t.me/Comp_Professors/84\n'
                             'https://t.me/Comp_Professors/35\n',
    'msg_masters_sedaghat': '👨🏻‍🏫استاد یاسر صداقت\n'
                            ' ۰۵۱-۳۸۸۰۵۱۴۸ ☎️\n'
                            'y_sedaghat@um.ac.ir 📧\n'
                            'تلگرام : @y_sedaghat\n'
                            '🗄تحصیلات: \n'
                            '\t🔰مرتبه علمی: استادیار\n'
                            '\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر - معماری کامپیوتر\n'
                            '\t🔰محل اخذ آخرین مدرک تحصیلی: دانشگاه صنعتی شریف، تهران، ایران\n'
                            '\n✅سطح تدریس : پیشرفته\n'
                            '✅نمره دهی : خوب\n'
                            '🏷توضیحات: \n بجز حساسیت های الکیی ک داره دقیقا رو نظم و با برنامه و خیلی هم خوب تدریس میکنه n\
                            در این حد ک ارشادی جزوه صداقت رو درس میداد(۳ فصل آخرشو) \n '
                            'کلی هم نمره اضافه داره صداقت، کلاسای حل تمرینش همش امتیازیه 4و5 تا کوییز امتیازی داره \n '
                            'از اول ترم مشخص میکنه برنامشو طبق همون میره جلو\n '
                            '\nنظرات دانشجویان💡 : \n'
                            'https://t.me/ashnayi_ba_asatid/483\n'
                            'https://t.me/Comp_Professors/21\n'
                            'https://t.me/Comp_Professors/36\n'
                            'https://t.me/Comp_Professors/25 (روش پژوهش)\n'
                            'https://t.me/Comp_Professors/48 (روش پژوهش)\n',
    'msg_masters_nori': '🔎اطلاعات مربوطه استاد نوری، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_bafghi': '👨🏻‍🏫استاد قائمی بافقی\n'
                          '۰۵۱-۳۸۸۰۵۰۶۲ ☎️\n'
                          ' ghaemib@um.ac.ir 📧\n'
                          '🗄تحصیلات: \n'
                          '\t\t\t🔰مرتبه علمی: دانشیار\n'
                          '\t\t\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر - نرم افزار\n'
                          '\t\t\t🔰محل اخذ آخرین مدرک تحصیلی: دانشگاه صنعتی امیرکبیر، تهران، ایران\n\n'
                          '🏷توضیحات : \n استاد بیشترِ مباحث رو تدریس می کنه، یعنی از هر چیزی در حد نیاز میگه، مثلا '
                          'در درس گسسته مباحثی مانند مرتبه زمانی و ساختمان داده هم بیان میکنه. در بیان مطلب و تدریس '
                          'ضعیف هستند، در حدی که باید خودت بخونی 🙃 سرعت تدریسشون هم بالاس و رو یه مبحث نمیمونن\n'
                          'در ضمن تلگرام هم ندارن:) راه های ارتباطی ایمیل و سروش و واتس اپ :) \n'
                          '\nنظرات دانشجویان💡 : \n'
                          'https://t.me/Comp_Professors/58\n'
                          'https://t.me/Comp_Professors/64\n'
                          'https://t.me/Comp_Professors/31\n',
    'msg_masters_tosi': '👨🏻‍🏫استاد هاله امین طوسی\n'
                        ' ۰۵۱-۳۸۸۰۵۴۳۶ ☎️\n'
                        'amintoosi@um.ac.ir 📧\n'
                        '🗄تحصیلات: \n'
                        '\t🔰مرتبه علمی: استادیار\n'
                        '\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر\n'
                        '\t🔰محل اخذ آخرین مدرک تحصیلی: محل اخذ آخرین مدرک تحصیلی: دانشگاه نيوساوت ولز، استرالیا\n',
    'msg_masters_harati': '🔎اطلاعات مربوطه استاد هراتی، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_paydar': '👨🏻‍🏫صمد پایدار\n'
                          ' ۰۵۱-۳۸۸۰۵۱۸۴ ☎️\n'
                          's-paydar@um.ac.ir 📧\n'
                          'تلگرام : @samadpaydar\n'
                          '🗄تحصیلات: \n'
                          '\t🔰مرتبه علمی: استادیار\n'
                          '\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر - معماری کامپیوتر\n'
                          '\t🔰محل اخذ آخرین مدرک تحصیلی: دانشگاه صنعتی شریف، تهران، ایران\n'
                          '\n✅سطح تدریس : خوب\n'
                          '✅نمره دهی : خوب\n'
                          '🏷توضیحات : \n نحوه درس دادن و انتقال مفاهیم خوب 👌🏻 کارگاه ها خودشون هم میان'
                          ' تمریناتی که سر کلاس میدن کاملا مرتبط با شی گرایی هست و شی گرایی رو'
                          ' فدای الگوریتم های پیچیده و سوالات پیچیده که میشه بدون شی گرایی هم حلشون کرد نمیکنن. '
                          '\nنظرات دانشجویان💡 : \n'
                          'https://t.me/Comp_Professors/45\n'
                          'https://t.me/Comp_Professors/46\n',
    'msg_masters_mirzavaziri': '🔎اطلاعات مربوطه استاد پایدار، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_ghiasi': '👨🏻‍🏫سید کمال الدین غیاثی شیرازی\n'
                          ' ۰۵۱-۳۸۸۰۵۱۵۸ ☎️\n'
                          'k.ghiasi@um.ac.ir 📧\n'
                          'تلگرام : @kghiasi\n'
                          '🗄تحصیلات: \n'
                          '\t🔰مرتبه علمی: استادیار\n'
                          '\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر\n'
                          '\t🔰محل اخذ آخرین مدرک تحصیلی: دانشگاه صنعتی امیرکبیر، تهران، ایران\n'
                          '\n✅سطح تدریس : عالی\n'
                          '\n✅سطح تدریس : خوب\n'
                          '🏷توضیحات: \n اخلاق و سطح ندریس و نظم عالی \n'
                          'واقعا جزؤ اساتیدیه که الویتش یادگیری دانشجوعه تمام تمرینات، امتحان ها و شیوه تدریسش '
                          'هم در این مسیره. تدریس مجازی به صورت ویدیو آفلاین بود که برای تهیه‌اش زحمات'
                          ' زیادی کشیده بودند. کلا استاد غیاثی انعطاف خوبی داشتن تو نمره دادن\n'
                          '\nنظرات دانشجویان💡 : \n'
                          'https://t.me/Comp_Professors/22'
                          'https://t.me/Comp_Professors/21\n'
                          'https://t.me/Comp_Professors/54\n'
                          'https://t.me/Comp_Professors/55\n',
    'msg_masters_fazlErsi': '🔎اطلاعات مربوطه استاد فضل ارثی، به زودی در این بخش قرار خواهد گرفت\n با تشکر🙏🏻',
    'msg_masters_zomorodi': '👨🏻‍🏫مریم زمردی مقدم\n'
                            '۰۵۱-۳۸۸۰۵۱۸۰ ☎️\n'
                            'm_zomorodi@um.ac.ir 📧\n'
                            '🗄تحصیلات: \n'
                            '\t🔰مرتبه علمی: استادیار\n'
                            '\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر - نرم افزار\n'
                            '\n✅سطح تدریس : متوسط رو به پایین\n'
                            '\nنظرات دانشجویان💡 : \n'
                            'https://t.me/Comp_Professors/97\n'
                            'https://t.me/Comp_Professors/29\n'
                            'https://t.me/Comp_Professors/82\n',
    'msg_masters_vahedian': '👨🏻‍🏫عابدین واحدیان مظلوم\n'
                            '۰۵۱-۳۸۸۰۵۰۵۳ ☎️\n'
                            'vahedian@um.ac.ir 📧\n'
                            'تلگرام : @dr_vahedian\n'
                            '🗄تحصیلات: \n'
                            '\t🔰مرتبه علمی: استادیار\n'
                            '\t🔰 آخرین مدرک تحصیلی : دکتری مهندسی برق\n'
                            '\t🔰 محل اخذ آخرین مدرک تحصیلی: دانشگاه نيوساوت ولز، استرالیا\n'
                            '\nنظرات دانشجویان💡 : \n'
                            'https://t.me/Comp_Professors/83 (زبان تخصصی)\n'
                            'https://t.me/Comp_Professors/27 (مدار)\n'
                            'https://t.me/Comp_Professors/20 (مدار)\n',
    'msg_masters_arban': '👨🏻‍🏫سعید عربان\n'
                         '۰۵۱-۳۸۸۰۵۱۲۰ ☎️\n'
                         'araban@um.ac.ir 📧\n'
                         'تلگرام : @Saeed_Araban\n'
                         '🗄تحصیلات: \n'
                         '\t🔰مرتبه علمی: استادیار\n'
                         '\t🔰 آخرین مدرک تحصیلی : دکتری مهندسی کامپیوتر - نر م افزار\n'
                         '\t🔰 محل اخذ آخرین مدرک تحصیلی: دانشگاه ملبورن، استرالیا\n'
                         'توضیحات : نظرات دانشجو هارو بخونید متوجه میشید :) \n'
                         '\nنظرات دانشجویان💡 : \n'
                         'https://t.me/Comp_Professors/96\n'
                         'https://t.me/Comp_Professors/96\n'
                         'https://t.me/Comp_Professors/38\n',
    'msg_masters_abrishami': '👨🏻‍🏫استاد سعید ابریشمی\n'
                             '۰۵۱-۳۸۸۰۵۱۲۱ ☎️\n'
                             'تلگرام : @Sabrishami\n'
                             's-abrishami@um.ac.ir 📧\n'
                             '🗄تحصیلات: \n'
                             '\t🔰مرتبه علمی: استادیار\n'
                             '\t🔰آخرین مدرک تحصیلی: دکترای مهندسی کامپیوتر - نرم افزار\n'
                             '\n✅سطح تدریس : پیشرفته\n'
                             '✅نمره دهی : خوب\n'
                             '\nنظرات دانشجویان💡 : \n'
                             'https://t.me/ashnayi_ba_asatid/358\n'
                             'https://t.me/Comp_Professors/63\n',
    'msg_masters_ershadi': '👨🏻‍🏫سارا ارشادی نسب\n'
                           '\nنظرات دانشجویان💡 : \n'
                           'https://t.me/ashnayi_ba_asatid/433\n'
                           'https://t.me/Comp_Professors/94\n'
                           'https://t.me/Comp_Professors/93\n'
                           'https://t.me/Comp_Professors/95\n',
    'msg_help': '''
        1️⃣. منابع و جزوات 
2️⃣. تمرین و امتحانات
3️⃣. گروه مهندسی کامپیوتر:
     🔘 اساتید
     🔘 انتشارات
     🔘 اخبار و اطلاعیه ها
4️⃣. ارسال فایل: میتوانید فایل درسی مورد نظر خود را برای ربات ارسال کنید تا در بخش درس مربوطه قرار گیرد
    ''',
    'btn_maaref_masters': '''
        #دیمه_کار
#تفسیر_نهج‌البلاغه 
خوش برخورد،حساس ب حضور غیاب 
ارائت خوب باشه تضمین پاسی 
میانترم تستی تشریحی 
پایانترم تستی
_________
#گندم_آبادی
#دانش_خانواده_وجمعیت
خوش اخلاق، جو کلاس عالی 
2 نمره مازاد کلاسی 
امتحان تستی معقول 
________
#علی_مشهدی
#حسین_پویا
خلاصه و مفید 👌♥️
هر چی ارائه داد بردارین 
همه جوره هوا دانشجو رو داره 
________
#محمد_باقر_رضاییان
#اندیشه_ها
درس دادن عالی، اهل غیبتی برندار 
حساس ب حضور غیاب +نمره مازاد 
درس دادن عالی 
Max:20
Min:10
Ave:16:5
 امتحان تستی معقول 
________
#ناهید_مشایی
#دانش_خانواده_وجمعیت
اخلاق عالی حساس به حضور غیاب
امتحان تشریحی تستی معقول 
بیان شیرین اصلا هم کلاس کسل کننده نیست 
________
#راضیه_آرام
#دانش_خانواده_وجمعیت 
نمره دادن خوبه 
کلاساش فانه، حساس ب حضور غیاب 
________
#نجف_زاده_تربتی
#اندیشه_ها 
حضور غیاب ب شدت حساس 
منبع کتاب معرفی شده +120 صفحه جزوه تایپی 
امتحان ب نسبت سخت 
________
#سبد_محمد_مرتضوی
#تفسیر
کلاس خسته کننده نیست 
حساس ب حضور غیاب دیر کردی راه نمیده 
امتحان نسبتا سخت از کتاب معرفی شده 
نمره دادن خوبه 
________
#مجتهدی
#تاریخ_امامت
حساس ب حضور غیاب
امتحان تستی نسبتا سخت 
نمودار داره 
فعال باشی بیست رو داری 
Max:20
Min:10
Ave:16
________
#حمید_رضا_ثنایی
#تاریخ_تحلیلی
کلاس کسل کننده 
نمره دادن افتضاح 
ب شدت حساس رو حضور غیاب
امتحان فضایی سوالات نکته دار 
________
#محمد_حسن_حایری
#اخلاق_اسلامی
در مجموع استاد خوبیه
حساس ب حضور غیاب 
خوش نمره خوش اخلاق 
امتحان تشریحی
Max:20
Min:13.5
Ave:18.46
____________
#مصطفی_گوهری_فخرآبادی
#تاریخ_امامت 
میانترم کوییز 25 صدمی سر کلاس که خیلی اسونه
حساس ب حضور غیاب 
نمره دادن خوبه
Max:20
Min:9.75
Ave:16.94
__________
#رویا_یداللهی
#فارسی_عمومی
استاد عالی 
کلاس فان 
خوش نمره 
__________
#مهدی_راشدی
#تفسیر 
حساس ب حضور غیاب 
+نمره مازاد
ارائه خوب باشه نمره بالا پاسی
نمره دهی خوبه 
________
#جباریان
#دانش_خانواده_وجمعیت 
حضور غیاب نداره 
کلاس فان امتحان 40 تا تست 
از مباحث کتاب و مطرح شده در کلاس
ارائه تا 4 نمره 
________
#عبدالقاسم_کریمی
کلا برندارین 💩😃
امتحان تستی تشریحی سخت
از اونا که با پنبه (خنده هاش) سر میبره 
_________
#سید_حسین_موسوی
#اخلاق_اسلامی 
حضور غیاب ب شدت حساس
نمره دهی عالی 
امتحان تستی در حد معقول و متوسط 
________
#علیرضا_آزاد
#تفسیر 
نمره مازاد تا دلت بخواد
حساس ب حضور غیاب
امتحان در حد کتاب معرفی شده و مباحث کلاسی
نمودار داره 
Max:20
Min:0
Ave:18
________

#صدیقه_صراف_نژاد
#دانش_خانواده_وجمعیت 
حساس ب حضور غیاب 
+نمره مازاد 
ارائه داره 
امتحان تستی 40 تا
خوش نمره 
________

#احمد_پور_فرخنده
#تاریخ_تحلیلی 
حساس ب حضور غیاب 
گویا رندوم هم حضور غیاب میکنن
کلاس کسل کننده 
امتحان سخت 
نمره دهی تعریفی نداره 
فقط اینکه کسی رو نمیندازه 
________

#علیرضا_محمدی
#انقلاب
#اندیشه_ها
خوش اخلاق کلاس کسل کننده نیست
خوش نمره 
فعال باشی بالا 18
Max:20
Min:12
Ave:18.87
________
#نوعی_باغبان
#انقلاب
از هر نظر عالی 🌹سواد و تدریس و اخلاق و نمره دهی
    ''',
    'btn_college': 'گروه مهندسی کامپیوتر🏫',
    'btn_exams_exe': 'تمرین و امتحانات📑',
    'btn_sources': 'منابع و جزوات📚',
    'btn_plans': 'طرح های پژوهشی جاری',
    'btn_send_document': 'ارسال فایل📤',
    'btn_contact': '📞تماس با من👨🏻‍💻',
    'btn_help': 'راهنمایی✅',

    'btn_college_masters': 'اساتید👨🏻‍🏫',
    'btn_college_news': 'اخبار📰',
    'btn_college_notification': 'اطلاعیه ها🔖',
    'btn_college_conference': 'کنفرانس ها و همایش ها🎥',
    'btn_college_about': 'درباره ما',
    'btn_college_pack': '📦بسته های کارشناسی',
    'btn_college_contact': 'راه های ارتباطی دانشکده📞',
    'btn_college_teach': 'آموزش',
    'btn_file_input': 'ارسال فایل',
    'btn_college_press': 'انتشارات📑',
    'btn_college_press_latinArticle': 'مقالات لاتین🧾',
    'btn_college_press_persianArticle': 'مقالات فارسی',
    'btn_college_press_books': 'کتاب ها📚',

    'btn_add_master': '+اضافه کردن استاد',
    'btn_add_subject': 'اضافه کردن درس+',

    'btn_exe_fundamental_programming': 'مبانی برنامه نویسی ابریشمی',
    'btn_exe_advance_programming': 'برنامه سازی پیشرفته پایدار',
    'btn_exe_discrete_bafghi': 'ریاضیات گسسته بافقی',
    'btn_exe_discrete_structure': 'ساختمان گسسته',
    'btn_exe_differential_equation': 'معادلات دیفرانسیل',
    'btn_exe_data_structure': '-ساختمان داده-',

    'btn_src_fundamental_programming': 'مبانی کامپیوتر برنامه نویسی',
    'btn_src_advance_programming': 'برنامه سازی پیشرفته',
    'btn_src_ai_abrishami': 'هوش مصنوعی(ابریشمی)',
    'btn_src_os_allahbakhsh': 'سیسستم عامل(الله بخش)',
    'btn_src_discrete': 'ریاضیات گسسته',
    'btn_src_differential_equation': '-معادلات دیفرانسیل',
    'btn_src_data_structure': 'ساختمان داده',

    'btn_back_home': 'خانه🏠',
    'btn_back_college': 'بازگشت🔙',
}

FIRST, SECOND = range(2)
logging.basicConfig(filename='info.log', filemode='a', level=logging.INFO,
                    format='%(asctime)s-%(filename)s-%(message)s-%(funcName)s')


def start(update, context):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    group_name = update.message.chat.title
    group_id = update.message.chat.id
    # write user data in file
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    if update.message.chat.type == "group" and (group_name == 'SV' or group_name == 'CE@FUM<99> group'):
        context.bot.send_message(chat_id=update.effective_chat.id, text='چند بار start میزنی داش :|')
        return 'out!start'
    if update.message.chat.type == "private":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=messages['msg_start_private'].format(first_name))
    elif update.message.chat.type == "group":
        context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_start_group'].format(group_name))
    elif update.message.chat.type == "supergroup":
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=messages['msg_start_supergroup'].format(group_name))
    elif update.message.chat.type == "channel":
        context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_start_channel'])

    main_menu_handler(update, context)
    context.bot.send_message(chat_id=131605711, text=str(update))
    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))


def main_menu_handler(update, context):
    buttons = [
        [messages['btn_exams_exe'], messages['btn_sources']],
        [messages['btn_college'], messages['btn_send_document']],
        [messages['btn_contact'], messages['btn_help']],
    ]
    update.message.reply_text(
        text=messages['msg_main_handler'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def exe_subject_handler(update, context):
    buttons = [
        [messages['btn_exe_fundamental_programming'], messages['btn_exe_advance_programming']],
        [messages['btn_exe_discrete_bafghi'], messages['btn_exe_discrete_structure']],
        [messages['btn_exe_data_structure'], messages['btn_exe_differential_equation']],
        [messages['btn_back_home']],
    ]
    update.message.reply_text(
        text=messages['msg_select_exe_subject'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


#  [messages['btn_src_ai_abrishami'], messages['btn_src_os_allahbakhsh']],
#  [messages['btn_src_differential_equation']],


def src_subject_handler(update, context):
    buttons = [
        [messages['btn_src_discrete'], messages['btn_src_data_structure']],
        [messages['btn_src_fundamental_programming'], messages['btn_src_advance_programming']],
        [messages['btn_back_home']],
    ]
    update.message.reply_text(
        text=messages['msg_select_src_subject'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def college_handler(update, context):
    buttons = [
        [messages['btn_college_news'], messages['btn_college_press']],
        [messages['btn_college_teach'], messages['btn_college_masters'], messages['btn_college_notification']],
        [messages['btn_college_about'], messages['btn_college_contact']],
        [messages['btn_back_home']],
    ]
    update.message.reply_text(
        text=messages['msg_college'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


# ToDo get persian articles and books
def college_getLatinArticles():
    url = ARTICLES_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    number_result = soup.find_all('td', attrs={
        'style': 'padding:5px; border:1px solid #E6E6E6; text-align:center !important;'})
    title_result = soup.find_all('td', attrs={
        'style': 'padding:5px; border:1px solid #E6E6E6; text-align: justify !important; direction: ltr; '})
    date_result = soup.find_all('td', attrs={'style': 'padding:5px; border:1px solid #E6E6E6;'})
    author_result = soup.find_all('td', attrs={'style': 'padding:5px; border:1px solid #E6E6E6;'})
    authors = [item.text for item in author_result]  # odds
    date = [item.text for item in date_result]  # even
    titles = [item.text for item in title_result]
    links = [item.a['href'] for item in title_result]
    return authors, titles, date, links


def college_latinArticles_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    authors, titles, date, links = college_getLatinArticles()
    txt = ''
    for t, a, d, l in list(zip(titles[:10], authors[1:20:2], date[0:20:2], links[:10])):
        txt += '📝{0} - <a href="{3}">{1}</a> - {2} \n'.format(a, t, d, l)
    buttons = [
        [InlineKeyboardButton('مراجعه به سایت', 'http://ce.um.ac.ir/index.php?option=com_groups&view=enarticles&'
                                                'edugroups=3105&cur_stu_title=&Itemid=694&lang=fa')],
    ]
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    update.message.reply_text(text=txt, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(buttons))


# def college_articles_keyboard(update: Update, context: CallbackContext) -> None:
#     query = update.callback_query
#     data = query.data
#     chat_id = query.message.chat_id
#     message_id = query.message.message_id
#     authors, titles, date, links = college_getLatinArticles()
#     txt = ''
#     for t, a, d, l in list(zip(titles[:15], authors[1:30:2], date[0:30:2], links[:15])):
#         txt += '📝{0} - <a href="{3}">{1}</a> - {2} \n'.format(a, t, d, l)
#     txt += '\n<a href="{}">مراجعه به سایت</a>\n'.format(ARTICLES_URL)
# button = [
#     [InlineKeyboardButton('مراجعه به سایت', 'http://ce.um.ac.ir/index.php?option=com_groups&view=enarticles&'
#                                             'edugroups=3105&cur_stu_title=&Itemid=694&lang=fa')],
# ]
# if data == 'extraArticles':
#     context.bot.send_chat_action(chat_id, ChatAction.TYPING)
#     context.bot.editMessageText(text=txt, chat_id=chat_id, message_id=message_id)
# context.bot.editMessageReplyMarkup(text=txt + '\n<a href="{}">مقالات بیشتر</a>\n'.format(ARTICLES_URL),
#                                    parse_mode=ParseMode.HTML,
#                                    reply_markup=InlineKeyboardMarkup(button),
#                                    chat_id=chat_id, message_id=message_id)


def college_persianArticles_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='به زودی فایل های مربوطه در این بخش قرار خواهند '
                                                                    'گرفت،\n با تشکر🙏🏻 ')


def college_books_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='به زودی فایل های مربوطه در این بخش قرار خواهند '
                                                                    'گرفت،\n با تشکر🙏🏻 ')


def college_press_handler(update: Update, context: CallbackContext) -> None:
    buttons = [
        [messages['btn_college_press_latinArticle'], messages['btn_college_press_books']],
        [messages['btn_college_press_persianArticle']],
        [messages['btn_back_home'], messages['btn_back_college']],
    ]
    update.message.reply_text(
        text=messages['msg_college_press'],
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )


def college_news_handler(update, context):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    url = BASE_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_result = soup.find_all('div', attrs={'class': 'aidanews2_positions'})
    title = [item.h1.a.text for item in title_result]
    date_time_result = soup.find_all('div', attrs={'class': 'aidanews2_botL'})
    date_time = [item.span.text for item in date_time_result]
    links = [item.h1.a['href'] for item in title_result]
    txt = ''
    for i in range(len(date_time) - 1):
        txt += '{}📌'.format(i + 1) + '<a href="ce.um.ac.ir{}">{}</a>'.format(links[i], title[i]) + '\n\t' + date_time[
            i] + '\n'
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    button = [
        [InlineKeyboardButton('مشاهده همه ی اخبار', 'http://ce.um.ac.ir/index.php?option=com_content&view=category'
                                                    '&id=102&Itemid=634&lang=fa')],
    ]
    update.message.reply_text(
        text=txt, parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(button)
    )
    context.bot.send_message(chat_id=131605711, text=str(update))
    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))


def college_notification_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    url = BASE_URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_result = soup.find_all('div', attrs={'class': 'aidanews2_positions'})
    title = [item.h1.a.text for item in title_result]
    links = [item.h1.a['href'] for item in title_result]
    date_time_result = soup.find_all('span', attrs={'class': 'aidanews2_date'})
    date_time = [item.text for item in date_time_result]
    txt = ''
    for i in range(5, len(date_time)):
        txt += '{}📌'.format(i - 4) + '<a href="ce.um.ac.ir{}">{}</a>'.format(links[i], title[i]) + \
               '\n\t' + date_time[i] + '\n'
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    button = [
        [InlineKeyboardButton('مشاهده همه ی اطلاعیه ها', 'http://ce.um.ac.ir/index.php?option=com_content&view=category'
                                                         '&id=113&Itemid=540&lang=fa')],
    ]
    update.message.reply_text(
        text=txt, parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(button)
    )


def college_teach_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='به زودی فایل های مربوطه در این بخش قرار خواهند '
                                                                    'گرفت،\n با تشکر🙏🏻 ')


def college_masters_handler(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    buttons = [
        [
            InlineKeyboardButton('برنامه سازی پیشرفته', callback_data='advance_programming'),
            InlineKeyboardButton('مدار منطقی', callback_data='logic_circuits'),
        ], [
            InlineKeyboardButton('مبانی کامپیوتر و برنامه سازی', callback_data='fundamental_programming'),
            InlineKeyboardButton('ریاضیات گسسته', callback_data='discrete_math'),
        ], [
            InlineKeyboardButton('زبان تخصصی', callback_data='advance_english'),
            InlineKeyboardButton('طراحی الگوریتم', callback_data='algorithm'),
            InlineKeyboardButton('ساختمان داده', callback_data='data_structure'),
        ], [
            InlineKeyboardButton('معارف', callback_data='maaref'),
            InlineKeyboardButton('اضافه کردن درس +', callback_data='add_subject')
        ]
    ]
    update.message.reply_text(
        text='درس مورد نظر را انتخاب کنید:',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return FIRST


def college_masters_ds_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('دکتر غیاثی شیرازی', callback_data='ghiasi'),
            InlineKeyboardButton('دکتر امین طوسی', callback_data='tosi'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_algorithm_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('دکتر نوری بایگی', callback_data='noriBaigi'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_ap_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('دکتر نوری بایگی', callback_data='noriBaigi'),
            InlineKeyboardButton('دکتر پایدار', callback_data='paydar'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_discrete_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('دکتر بافقی', callback_data='bafghi'),
            InlineKeyboardButton('دکتر غیاثی شیرازی', callback_data='ghiasi'),
        ], [
            InlineKeyboardButton('مجید میرزاوزیری', callback_data='mirzavaziri'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_logic_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('یاصر صداقت', callback_data='sedaghat'),
            InlineKeyboardButton('سارا ارشادی نسب', callback_data='ershadi'),
        ], [
            InlineKeyboardButton('مریم زمردی مقدم', callback_data='zomorodi'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_fp_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('سعید ابریشمی', callback_data='abrishami'),
            InlineKeyboardButton(' نوری بایگی', callback_data='noriBaigi'),
        ], [
            InlineKeyboardButton('احسان فضل ارثی', callback_data='fazlErsi'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_advEnglish_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # data = query.data
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    buttons = [
        [
            InlineKeyboardButton('سعید عربان', callback_data='arban'),
            InlineKeyboardButton('عابدین واحدیان مظلوم', callback_data='vahedian'),
        ], [
            InlineKeyboardButton(messages['btn_add_master'], callback_data='add_master')
        ]
    ]
    context.bot.editMessageText(text='برای دریافت اطلاعات، استاد مورد نظر را انخاب کنید:',
                                chat_id=chat_id, message_id=message_id,
                                reply_markup=InlineKeyboardMarkup(buttons))
    return SECOND


def college_masters_maaref_handler(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id, text=messages['msg_maaref_masters'])
    return SECOND


def end_college_masters_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    first_name = query.message.chat.first_name
    last_name = query.message.chat.last_name
    # message_id = query.message.message_id
    if data == 'abrishami':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://s-abrishami.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_abrishami'], reply_markup=InlineKeyboardMarkup(button))
        # context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_masters_abrishami'])
        # context.bot.editMessageText(text=messages['msg_masters_abrishami'], chat_id=chat_id, message_id=message_id)
    elif data == 'noriBaigi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://nouribaygi.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_noriBaigi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'paydar':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://s-paydar.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_paydar'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'fazlErsi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://fazlersi.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_fazlErsi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'sedaghat':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://y_sedaghat.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_sedaghat'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'ershadi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_masters_ershadi'])
    elif data == 'bafghi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://ghaemib.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_bafghi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'ghiasi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://profsite.um.ac.ir/~k.ghiasi/')]]
        query.message.reply_text(text=messages['msg_masters_ghiasi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'harati':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://a.harati.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_harati'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'tosi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://amintoosi.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_tosi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'arban':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://araban.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_arban'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'zomorodi':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://m_zomorodi.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_zomorodi'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'vahedian':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        button = [[InlineKeyboardButton('صفحه شخصی', 'http://vahedian.profcms.um.ac.ir/')]]
        query.message.reply_text(text=messages['msg_masters_vahedian'], reply_markup=InlineKeyboardMarkup(button))
    elif data == 'mirzavaziri':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_masters_mirzavaziri'])
    elif data == 'add_master':
        context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text='اگر استاد مد نظر در لیست وجود ندارد، میتوانید'
                                                                        'اسم استاد را فقط با فرمت زیر(بین دو خط تیره)'
                                                                        ' ارسال کنید 🙏🏻: '
                                                                        '\n -نام استاد-')
        get_master(update, context)
    context.bot.send_message(chat_id=131605711, text=str(update))
    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))
    # return ConversationHandler.END


def get_master(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, text='نام استاد دریافت شد✅پس از تایید در بات قرار داده میشود')
    context.bot.send_message(chat_id=131605711, text=update.message.text)


def college_masters_add_subject(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.editMessageText(chat_id=update.effective_chat.id, message_id=message_id,
                                text='اگر درس مد نظر در لیست وجود ندارد، میتوانید'
                                     'نام درس را فقط با فرمت زیر(بین دو آندرلاین)'
                                     ' ارسال کنید 🙏🏻: '
                                     '\n _نام درس_')


def get_subject(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id, text='نام درس دریافت شد✅پس از تایید در بات قرار داده میشود')
    context.bot.send_message(chat_id=131605711, text=update.message.text)


def college_contact_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    URL = BASE_URL
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    contact_result = soup.find_all('ul', attrs={'class': 'contact-info'})
    contact_info = [item.li.text for item in contact_result]
    txt = '📍آدرس : {}'.format(contact_info) + '\n\n' + messages['msg_college_contact']
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
    buttons = [
        [InlineKeyboardButton('سایت مهندسی کامپیوتر', 'http://ce.um.ac.ir/index.php?lang=fa')],
        [InlineKeyboardButton('شماره تلفن های گروه کامپیوتر', 'http://118.um.ac.ir/%D8%AF%D8%A7%D9%86%D8%B4%DA%A9%D8%AF'
                                                              '%D9%87-%D9%87%D8%A7/%D8%AF%D8%A7%D9%86%D8%B4%DA%A9%D8%AF'
                                                              '%D9%87-%D9%85%D9%87%D9%86%D8%AF%D8%B3%DB%8C.html')],
    ]
    update.message.reply_text(text='پیوندها: ', reply_markup=InlineKeyboardMarkup(buttons))


def college_about_handler(update, context):
    # todo fix web scraping
    # url = BASE_URL
    # response = requests.get(url)
    # soup = BeautifulSoup(response.content, 'html.parser')
    # about_result = soup.find_all('div', attrs={'class': 'item-page'})
    # about_txt = [item.text for item in about_result]
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    button = [
        [InlineKeyboardButton('اطلاعات بیشتر', 'http://ce.um.ac.ir/index.php?option=com_content&view=article&id=134&'
                                               'Itemid=521&lang=fa')],
    ]
    update.message.reply_text(text=messages['msg_college_about'], reply_markup=InlineKeyboardMarkup(button))


def contact_handler(update, context):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    buttons = [
        [
            InlineKeyboardButton('telegram', 'https://telegram.me/soroush_fathi'),
            InlineKeyboardButton('instagram', 'https://instagram.com/soroushfathi.pb')
        ], [
            InlineKeyboardButton('LinkedIn', 'www.linkedin.com/in/soroush-fathi-45aa07201'),
            InlineKeyboardButton('github', 'https://github.com/soroushfathi'),
        ]
    ]
    update.message.reply_text(text=messages['msg_contact'], reply_markup=InlineKeyboardMarkup(buttons))
    context.bot.send_message(chat_id=131605711, text=str(update))
    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))


def help_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_PHOTO)
    context.bot.send_message(chat_id=update.effective_chat.id, text=messages['msg_help'])


def back_home_handler(update: Update, context: CallbackContext) -> None:
    main_menu_handler(update, context)


def back_college_handler(update: Update, context: CallbackContext) -> None:
    college_handler(update, context)


def src_fp_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIOJ2EvuoLom5UGUamAJyt1Vh-jKhrw'
                                                                         'AAJ4DAACvnOBUVgDsjQ4o52yIAQ',
                              filename='Fundamental Programming Sources.zip',
                              caption='کناب دایتل و جزوات', timeout=300)
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIONGEvvpe8Ed50EiOROx9N9kq6'
                                                                         '1sNdAAJ6DAACvnOBUc5tmQ3nPxXFIAQ',
                              filename='Sample Codes.zip',
                              caption='نمونه کد های مسائل کارگاه', timeout=300)
    # with open('./slides-abrishami.zip') as f:
    #     context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    #     print(context.bot.send_document(chat_id=update.effective_chat.id, document=f,
    #                                     filename='Slides DR.Abrishami',
    #                                     caption='اسلاید های استاد ابریشمی', timeout=3000))


def src_discrete_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIONmEvv79XY_bXBpIhlnDNMqbMNm9'
                                                                         'EAAJ7DAACvnOBUeySzm0kBgeOIAQ',
                              filename='Rosen Discrete Mathematics.pdf',
                              caption='منبع اصلی - روزن', timeout=3000)
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAION2EvwEM1JXSHvis_Pl9MHo'
                                                                         'DbwkNDAAJ9DAACvnOBUcV2FFEF0FoPIAQ',
                              filename='Solution Manual for Discrete Mathematics Rosen.pdf',
                              caption='پاسخنامه روزن', timeout=3000)


def src_ap_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='این بخش در حال بروزرسانی است، به زودی فایل های'
                                                                    ' مربوطه قرار خواهند گرفت')


def src_ds_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    #  buttons for linking DS videos to programming telegram channel
    buttons = [
        [  # first row
            InlineKeyboardButton('قسمت1', 'https://t.me/Azad_Developers/17205'),
            InlineKeyboardButton('قسمت2', 'https://t.me/Azad_Developers/17209'),
            InlineKeyboardButton('قسمت3', 'https://t.me/Azad_Developers/17214'),
        ], [
            InlineKeyboardButton('قسمت4', 'https://t.me/Azad_Developers/17229'),
            InlineKeyboardButton('قسمت5', 'https://t.me/Azad_Developers/17235'),
            InlineKeyboardButton('قسمت6', 'https://t.me/Azad_Developers/17243'),
        ], [
            InlineKeyboardButton('قسمت7', 'https://t.me/Azad_Developers/17248'),
            InlineKeyboardButton('قسمت8', 'https://t.me/Azad_Developers/17264'),
            InlineKeyboardButton('قسمت9', 'https://t.me/Azad_Developers/17279'),
        ], [
            InlineKeyboardButton('قسمت10', 'https://t.me/Azad_Developers/17298'),
            InlineKeyboardButton('قسمت11', 'https://t.me/Azad_Developers/17318'),
            InlineKeyboardButton('قسمت12', 'https://t.me/Azad_Developers/17328'),
        ], [
            InlineKeyboardButton('قسمت13', 'https://t.me/Azad_Developers/17344'),
            InlineKeyboardButton('قسمت14', 'https://t.me/Azad_Developers/17361'),
            InlineKeyboardButton('قسمت15', 'https://t.me/Azad_Developers/17373'),
        ], [
            InlineKeyboardButton('قسمت16', 'https://t.me/Azad_Developers/17386'),
            InlineKeyboardButton('قسمت17', 'https://t.me/Azad_Developers/17401'),
            InlineKeyboardButton('قسمت18', 'https://t.me/Azad_Developers/17415'),
        ], [
            InlineKeyboardButton('قسمت19', 'https://t.me/Azad_Developers/17428'),
            InlineKeyboardButton('قسمت20', 'https://t.me/Azad_Developers/17448'),
            InlineKeyboardButton('قسمت21', 'https://t.me/Azad_Developers/17464'),
        ], [
            InlineKeyboardButton('قسمت22', 'https://t.me/Azad_Developers/17479'),
            InlineKeyboardButton('قسمت23', 'https://t.me/Azad_Developers/17493'),
            InlineKeyboardButton('قسمت24', 'https://t.me/Azad_Developers/17505'),
        ], [
            InlineKeyboardButton('قسمت25', 'https://t.me/Azad_Developers/17537'),
            InlineKeyboardButton('قسمت26', 'https://t.me/Azad_Developers/17584'),
            InlineKeyboardButton('قسمت27', 'https://t.me/Azad_Developers/17595'),
        ], [
            InlineKeyboardButton('قسمت28', 'https://t.me/Azad_Developers/17602'),
            InlineKeyboardButton('قسمت29', 'https://t.me/Azad_Developers/17629'),
            InlineKeyboardButton('قسمت30', 'https://t.me/Azad_Developers/17633'),
        ], [
            InlineKeyboardButton('قسمت31', 'https://t.me/Azad_Developers/17647'),
            InlineKeyboardButton('قسمت32', 'https://t.me/Azad_Developers/17660'),
            InlineKeyboardButton('قسمت33', 'https://t.me/Azad_Developers/17670'),
        ], [
            InlineKeyboardButton('قسمت34', 'https://t.me/Azad_Developers/17727'),
            InlineKeyboardButton('قسمت35', 'https://t.me/Azad_Developers/17738'),
            InlineKeyboardButton('قسمت36', 'https://t.me/Azad_Developers/17755'),
        ],
        # [
        #     InlineKeyboardButton('قسمت37', 'https://t.me/Azad_Developers/17765'),
        #     InlineKeyboardButton('قسمت38', 'https://t.me/Azad_Developers/17773'),
        # ]
    ]
    update.message.reply_text(
        text='آموزش ساختمان داده(مدرس : سعید شهریوری):\n',
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIOIWEvqc_csllZ8y0oKN-rIQg'
                                                                         'LW8qhAAKZCwACvnOBUctL9li_jBvzIAQ',
                              filename='DS & Algorithm by Weiss',
                              caption='منبع درس ساختمان داده', timeout=11)

    logging.info('{} {}({}): {}\n'.format(first_name, last_name, chat_id, update))
    # with open('./sources/DS/The Art of Computer Programming (vol. 3_ Sorting and Searching) (2nd ed.) [Knuth '
    #           '1998-05-04].pdf') as f:
    #     context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    #     print(context.bot.send_document(chat_id=update.effective_chat.id, document=f,
    #                                     filename='The Art of Computer Programming',
    #                                     caption='منبع در ساختمان داده', timeout=300))


def src_ai_abrishami_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkBAAIUSWE1woC5Hbb05QH22qiZoYz-'
                                                                         'lN0SAAKwCQACUYl4USxYqCkiFX8gIAQ',
                              file_name='AI(abrishami)',
                              caption='فایل های درس هوش مصنوعی استاد ابریشمی بهار 1400')


def src_os_allah_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkBAAMNYTUlPxO9KFaay6vLcNKSEU-xmUwAA'
                                                                         'qYJAAJRiXhR3fEWYGFDKTYgBA',
                              file_name='OS(allah bakhsh)',
                              caption='فایل های درس سیستم عامل الله بخش بهار 1400')


def src_differential_equation(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkBAANAYTuhePSMSrMZU89512Jr-hnyK'
                                                                         'gADSQkAAiwg4VGEWVkaYkOiHyAE',
                              file_name='معادلات دیفرانسیل ادوارز و پتی')
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkBAANCYTuiCtYpXKvCyNvLaEIYtD4X84Y'
                                                                         'AAkoJAAIsIOFRWMo8c14kmQsgBA',
                              file_name='پاسخ نامه معادلات دیفرانسیل ادوارز و پتی')


# Start exam file handlers
def exam_ap_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
        context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIOA2EvpGPuvMDrLtioE7S4d'
                                                                             'plwkDZtAAKGCwACvnOBURIJI-dSD7TGIAQ',
                                  filename='AP exams.zip',
                                  caption='سوالات امتحانی برنامه سازی پیشرفته دکتر پایدار', timeout=60)
    except error.NetworkError as e:
        update.message.reply_text(text=messages['msg_network_error'])


def exam_discrete_bafghi_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT, timeout=300)
        context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIOGWEvqEl-8BKckRp3oqlRQZE'
                                                                             'fettOAAKWCwACvnOBUQP4XT_T7-rsIAQ',
                                  filename='Discrete exams & exe (Bafghi)',
                                  caption='تمرینات و امتحانات ریاضیات گسسته استاد بافقی', timeout=200)
    except error.NetworkError as e:
        update.message.reply_text(text=messages['msg_network_error'])


def exam_discrete_structure_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    try:
        context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT, timeout=300)
        context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkDAAIOF2Evp3rOZ4ILOBWni6xh3Y97y'
                                                                             'ud6AAKUCwACvnOBUdfT2nMzrPC9IAQ',
                                  filename='Discrete Structure', caption='تمرینات ساختمان گسسته', timeout=300)

    except error.NetworkError as e:
        update.message.reply_text(text=messages['msg_network_error'])


def exam_fp_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='این بخش در حال بروزرسانی است، به زودی فایل های'
                                                                    ' مربوطه قرار خواهند گرفت')


def exam_ds_file_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.UPLOAD_DOCUMENT)
    context.bot.send_document(chat_id=update.effective_chat.id, document='BQACAgQAAxkBAAIUVWE1xLqU2lUhw1O_toh68mkaFXe'
                                                                         '2AAKRCwAC5miwUTynOJTv3cEYIAQ',
                              filename='DS Ghiasi',
                              caption='فایل درس ساختمان داده غیاثی 99', timeout=60)


def exam_differential_equation(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id=update.effective_chat.id, text='کانال حل تمرین نمونه سوالات(محمدیان):\n'
                                                                    'https://t.me/tamrin_moadelat_fum')


# TODO InlineQueryResultGif


def send_document_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    context.bot.send_chat_action(chat_id, ChatAction.TYPING)
    context.bot.send_message(chat_id, text=messages['msg_send_document'].format(first_name))


# send files which given from user for me(chat id=131605711)
def docmsg(update: Update, context: CallbackContext):
    context.bot.send_document(chat_id=131605711, document=update.message.document.file_id)
    context.bot.send_message(chat_id=131605711, text=str(update))
    context.bot.send_message(chat_id=update.message.chat_id, text=messages['msg_send_document2'])


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query

    if query == "":
        return

    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Title",
            input_message_content=InputTextMessageContent(query.title()),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Caps",
            input_message_content=InputTextMessageContent(query.upper()),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Bold",
            input_message_content=InputTextMessageContent(
                f"*{escape_markdown(query)}*", parse_mode=ParseMode.MARKDOWN
            ),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Italic",
            input_message_content=InputTextMessageContent(
                # f"_{escape_markdown(query)}_", parse_mode=ParseMode.MARKDOWN
                '<i>{}</i>'.format(query), parse_mode=ParseMode.HTML
            ),
        ),
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Poem",
            input_message_content=InputTextMessageContent('<pre>{}</pre>'.format(query), parse_mode=ParseMode.HTML),
        ),
    ]
    update.inline_query.answer(results)


def sendpost(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=-1001342044227, text=update.channel_post.text)


def doc_sender(update: Update, context: CallbackContext) -> None:
    if update.channel_post.document:
        context.bot.send_document(chat_id=-1001342044227, document=update.channel_post.document.file_id, caption=update.channel_post.caption)
    elif update.channel_post.photo:
        context.bot.send_photo(chat_id=-1001342044227, photo=update.channel_post.photo[0].file_id, caption=update.channel_post.caption)
    elif update.channel_post.video:
        context.bot.send_video(chat_id=-1001342044227, video=update.channel_post.video.file_id, caption=update.channel_post.caption)
    elif update.channel_post.voice:
        context.bot.send_voice(chat_id=-1001342044227, voice=update.channel_post.voice.file_id, caption=update.channel_post.caption)
    elif update.channel_post.poll:
        context.bot.send_poll(chat_id=-1001342044227, question=update.channel_post.poll.question,
                              options=[item['text'] for item in update.channel_post.poll.options],
                              is_anonymous=update.channel_post.poll.question)
    elif update.channel_post.audio:
        context.bot.send_audio(chat_id=-1001342044227, audio=update.channel_post.audio, caption=update.channel_post.caption)


def main() -> None:
    """Run the Bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token='1914222564:AAE4nRZZZin810LKiGgw1woavSdVKvkDy9s', use_context=True)
    # request_kwargs={'proxy_url': 'https://t.me/proxy?server=162.55.171.113&port=443&secret=EE00000'
    #                                                    '000000000000000000000000000646c2e676f6f676c652e636f6d'}
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('exams_ap', exam_ap_file_handler))
    dispatcher.add_handler(CommandHandler('exams_dm', exam_discrete_structure_file_handler))

    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exams_exe']), exe_subject_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_advance_programming']), exam_ap_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_discrete_bafghi']),
                                          exam_discrete_bafghi_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_discrete_structure']),
                                          exam_discrete_structure_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_data_structure']), exam_ds_file_handler))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(messages['btn_exe_differential_equation']), exam_differential_equation))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_exe_fundamental_programming']),
                                          exam_fp_file_handler))

    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_send_document']), send_document_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_sources']), src_subject_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_data_structure']), src_ds_file_handler))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(messages['btn_src_differential_equation']), src_differential_equation))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_discrete']), src_discrete_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_ai_abrishami']), src_ai_abrishami_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_os_allahbakhsh']), src_os_allah_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_advance_programming']), src_ap_file_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_src_fundamental_programming']),
                                          src_fp_file_handler))

    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college']), college_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_news']), college_news_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_notification']),
                                          college_notification_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_press']), college_press_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_press_latinArticle']),
                                          college_latinArticles_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_press_persianArticle']),
                                          college_persianArticles_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_press_books']),
                                          college_books_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_contact']), college_contact_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_about']), college_about_handler))
    masters_conversation = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(messages['btn_college_masters']), college_masters_handler)],
        states={
            FIRST: [
                CallbackQueryHandler(college_masters_fp_handler, pattern="^fundamental_programming$"),
                CallbackQueryHandler(college_masters_discrete_handler, pattern="^discrete_math$"),
                CallbackQueryHandler(college_masters_ap_handler, pattern="^advance_programming$"),
                CallbackQueryHandler(college_masters_advEnglish_handler, pattern="^advance_english$"),
                CallbackQueryHandler(college_masters_logic_handler, pattern="^logic_circuits$"),
                CallbackQueryHandler(college_masters_ds_handler, pattern="^data_structure$"),
                CallbackQueryHandler(college_masters_algorithm_handler, pattern="^algorithm$"),
                CallbackQueryHandler(college_masters_maaref_handler, pattern="^maaref$"),
                CallbackQueryHandler(college_masters_add_subject, pattern="^add_subject$"),
            ],
            SECOND: [
                CallbackQueryHandler(end_college_masters_handler)
            ]
        },
        fallbacks=[MessageHandler(Filters.regex(messages['btn_college_masters']), college_masters_handler)],
        allow_reentry=True,
        # per_chat=True,
        # per_user=True,
        per_message=False,
    )
    dispatcher.add_handler(masters_conversation)
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_college_teach']), college_teach_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_back_college']), back_college_handler))

    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_back_home']), back_home_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_contact']), contact_handler))
    dispatcher.add_handler(MessageHandler(Filters.regex(messages['btn_help']), help_handler))

    dispatcher.add_handler(
        MessageHandler(Filters.regex(r'^-([ آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیئ\s\w]+)-$'), get_master))
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r'^_([ آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیئ\s\w]+)_$'), get_subject))
    dispatcher.add_handler(MessageHandler(Filters.document, docmsg))
    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    #  send channel posts to group
    dispatcher.add_handler(
        MessageHandler(Filters.regex(r'^(.[ آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهیئ\s\w\S\W@#$%^&*()_=+!]+.)$'), sendpost))
    dispatcher.add_handler(
        MessageHandler(Filters.document | Filters.photo | Filters.poll | Filters.voice | Filters.video
                       , doc_sender))
    # dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
    # Start hte Bot
    updater.start_polling()
    updater.idle()


main()

# token = '1914222564:AAFl7vn1ESo3oT9_65IicNKEWntq5RFuJOc'
# base_url = 'https://api.telegram.org/bot{}/getMe'.format(token)
# print(base_url)
# resp = requests.get(base_url)
# print(resp.text)
