import json
import time

import cv2
import numpy as np
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .captcha_prediction import NPTUCaptcha


class WebAp:
    def __init__(self, config_path, *args, user_agent='user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'):
        with open(config_path) as f:
            self.config = json.load(f)
        super().__init__(self.config["id"], self.config["pwd"], *args)
        self.account = args
        self.options = ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument(user_agent)
        self.captcha_cracker = NPTUCaptcha()

    def _get_captcha(self):
        # now that we have the preliminary stuff out of the way time to get that image :D
        captcha_element = self._wait_element(By.ID, "imgCaptcha")
        captcha_element.click()
        captcha_element = self._wait_element(By.ID, "imgCaptcha")
        img = cv2.imdecode(np.fromstring(captcha_element.screenshot_as_png, np.uint8), 1)
        return img

    def login(self, student_id, passward):
        self.captcha_cracker.load_NN()
        self._enter_login_page()
        while True:
            try:
                captcha_ans = self.captcha_cracker.get_ans(self._get_captcha())
                element = self._wait_element(By.ID, "LoginStd_txtCheckCode")
                element.send_keys(captcha_ans)
                element = self._wait_element(By.ID, "LoginStd_txtAccount")
                element.send_keys(student_id)
                element = self._wait_element(By.ID, "LoginStd_txtPassWord")
                element.send_keys(passward)
                element = self._wait_element(By.ID, "LoginStd_ibtLogin")
                element.click()
                user_menu = self._wait_element(By.CSS_SELECTOR, "frame[name='MENU']")
                return user_menu
            except UnexpectedAlertPresentException:
                print(UnexpectedAlertPresentException)
                self.browser.refresh()
                time.sleep(5)
                continue
        self.captcha_cracker.unload_NN()

    def logout(self):
        self.browser.switch_to_default_content()
        self.browser.switch_to.frame(self._wait_element(By.CSS_SELECTOR, "frame[name='MAIN']"))
        element = self._wait_element(By.ID, "CommonHeader_ibtLogOut")
        element.click()
        self.wait.until(EC.alert_is_present())
        alert = self.browser.switch_to.alert
        alert.accept()
        print("Logout at %s" % time.ctime())
        self.browser.quit()

    def _wait_element(self, *args):
        return self.wait.until(
            EC.presence_of_element_located(args))

    def _enter_login_page(self, webap_url="https://webap.nptu.edu.tw/web/Secure/default.aspx"):

        self.browser = Chrome(chrome_options=self.options)
        self.browser.get(webap_url)
        self.wait = WebDriverWait(self.browser, 3)

        menu = self._wait_element(By.CSS_SELECTOR, "[id*='ibtLoginStd']")
        menu.click()

    def _nav_to_menu(self, menu_id):
        user_menu = self.login(*self.account)
        self.browser.switch_to_default_content()
        self.browser.switch_to_frame(user_menu)
        labor_section = self._wait_element(By.ID, menu_id)
        labor_section.click()
        self.browser.switch_to_default_content()
        self.browser.switch_to_frame(self._wait_element(By.CSS_SELECTOR, "frame[name='MAIN']"))

    def test(self):
        while True:
            self._enter_login_page()
            captcha_ans = self.captcha_cracker.get_ans(self._get_captcha())
            element = self.wait.until(
                EC.presence_of_element_located((By.ID, "LoginStd_txtCheckCode")))
            element.clear()
            element.send_keys(captcha_ans)
            time.sleep(1)


if __name__ == '__main__':
    test_ap = WebAp()
    test_ap.test()
