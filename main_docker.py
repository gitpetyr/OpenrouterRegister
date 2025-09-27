from DrissionPage import ChromiumPage, ChromiumOptions
from pyvirtualdisplay import Display
import time,secrets,random
import os

display = Display(size=(1920, 1080))
display.start()

fn = secrets.token_hex(2)

def getTurnstileToken(page : ChromiumPage,times : int = 15):
    page.run_js("try { turnstile.reset() } catch(e) { }")

    turnstileResponse = None

    page.wait.ele_displayed("@name=cf-turnstile-response")

    for i in range(0, times):
        try:
            print("Finding Captcha")
            turnstileResponse = page.run_js("try { return turnstile.getResponse() } catch(e) { return null }")
            if turnstileResponse:
                print("Captcha Passed")
                return 
            
            try:
                page.wait.eles_loaded("@name=cf-turnstile-response",timeout=1.5,raise_err=True)
            except Exception:
                print("Couldn't find Captcha")
                return 
            
            challengeSolution = page.ele("@name=cf-turnstile-response")
            challengeWrapper = challengeSolution.parent()
            challengeIframe = challengeWrapper.shadow_root.ele("tag:iframe")
            
            challengeIframe.run_js("""
window.dtp = 1
function getRandomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// old method wouldn't work on 4k screens

let screenX = getRandomInt(800, 1200);
let screenY = getRandomInt(400, 600);

Object.defineProperty(MouseEvent.prototype, 'screenX', { value: screenX });

Object.defineProperty(MouseEvent.prototype, 'screenY', { value: screenY });
                        """)
            
            challengeIframeBody = challengeIframe.ele("tag:body").shadow_root
            challengeButton = challengeIframeBody.ele("tag:input")
            challengeButton.click()
            print("Try Captcha again")
        except:
            pass
        time.sleep(0.8)
    page.refresh()
    print("Trid Captcha")
    return 

class emailManger():
    def __init__(self):
        co = ChromiumOptions()
        co.set_argument("--no-sandbox")
        co.auto_port(True)
        co.incognito()
        co.set_timeouts(base=4)

        # change this to the path of the folder containing the extension
        EXTENSION_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "turnstilePatch"))
        co.add_extension(EXTENSION_PATH) 
        self.page = ChromiumPage(co)
        self.page.get("https://mail.chatgpt.org.uk/")
        self.page.wait.doc_loaded()
        self.page.wait(0.1,0.2)
        self.page.wait.ele_displayed("@class=email-address")
        self.email = self.page.ele("@class=email-address").text
    def refresh(self):
        self.page.refresh()
        self.page.wait.doc_loaded()
        self.page.wait(0.2,0.3)
    def renew(self):
        self.page.run_js("generateRandomEmail();")
        self.page.wait(0.7,0.8)
        self.email = self.page.ele("@class=email-address").text
    def geturl(self):
        self.refresh()
        time_start = time.time()
        self.page.wait(0.8,1.5)
        self.page.refresh()
        self.page.wait.doc_loaded()
        self.page.wait(1,2)
        self.page.wait.ele_displayed("@href:verify",timeout=15,raise_err=True)
        return self.page.ele("@href:verify").link
    def release(self):
        self.page.quit()

tmp_email = emailManger()

while True:
    try:
        tmp_email.renew()
        co = ChromiumOptions()
        co.set_argument("--no-sandbox")
        # co.set_browser_path("./Chromium.app/Contents/MacOS/Chromium")
        co.auto_port(True)
        co.incognito()

        co.set_timeouts(base=4)

        # change this to the path of the folder containing the extension
        EXTENSION_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "turnstilePatch"))
        co.add_extension(EXTENSION_PATH) 

        page1 = ChromiumPage(co)
        page1.get("https://openrouter.ai/")
        page1.wait.doc_loaded()

        page1.ele("@component=SignInButton").click()
        page1.wait.ele_displayed("@data-localization-key=signIn.start.actionLink",timeout=2,raise_err=True)
        page1.ele("@data-localization-key=signIn.start.actionLink").click()

        page1.ele("@id=emailAddress-field").input(tmp_email.email)
        password = secrets.token_hex(16)
        page1.ele("@name=password").input(password)
        page1.ele("@name=legalAccepted").check()
        page1.ele("@data-variant=solid").click()

        try:
            getTurnstileToken(page1)
        except:
            pass

        page1.wait.ele_displayed("@class:cl-formResendCodeLink",timeout=10,raise_err=True)
        page1.wait(0.4,0.5)
        page1.get(tmp_email.geturl())
        page1.wait.url_change("verify",exclude=True,timeout=4,raise_err=True)
        page1.wait.load_start()
        page1.wait.doc_loaded()
        page1.wait(0.3,0.5)
        page1.get("https://openrouter.ai/settings/keys")
        page1.wait.doc_loaded()
        #/html/body/div[6]/div/div/div/div[2]/div/div/div/div/div[4]/button
        #/html/body/div[6]/div/div/div/div[2]/div/div/div/div/div[4]/button
        page1.ele("@@tag()=button@@text():Create").click()
        page1.ele("@id=name").input(secrets.token_hex(16))#-4.flex.flex-row.justify-end > button
        page1.ele("@text()=Create").click()
        api_key = page1.ele("@tag()=code").text
        print(api_key)
        open("/root/keys.txt",'a').write(api_key+"\n")
    except Exception as e:
        print(e)
        pass
    finally:
        page1.quit()
