import cv2
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import numpy as np
from .webap_login import WebAp
import imageio


class SelectCourse(WebAp):
    def _nav_to_courses(self):
        self._nav_to_menu("spnode_[A052]_線上選課")
        course_section = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#SubMenu_dgData > tbody > tr:nth-child(4 > td:nth-child(1) > a")))
        course_section.click()

    def _nav_to_common_course(self):
        com_course = self._wait_element(By.ID, "A0511S2Menu_lbt4")
        com_course.click()

    def _nav_to_general_course(self):
        com_course = self._wait_element(By.ID, "A0511S2Menu_lbt1")
        com_course.click()

    def _select_cat(self, com_type, option_value):
        cate = Select(self._wait_element(By.ID, "A0511S2_ddlWISH_CLASS_ID"))
        if com_type == "A":
            option_value = "ZZ001"
        elif com_type == "B":
            option_value = "ZZ002"
        elif com_type == "C":
            option_value = "ZZ003"
        elif com_type == "D":
            option_value = "ZZ004"
        elif com_type == "E":
            option_value = "ZZ005"
        cate.select_by_value(option_value)

    def _get_course(self, course_name, teacher_name):
        search_input = self._wait_element(By.ID, "A0511S2_txtSUBJ_CNAME")
        search_input.sendKeys(course_name)
        search_bt = self._wait_element(By.ID, "A0511S2_btnQuery")
        search_bt.click()
        course_tr = self.browser.find_elements_by_xpath(
                    "//tr[span[contains(text(),'%s')]]" % teacher_name)
        if len(course_tr) == 0:
            print("查不到%s的%s" % (teacher_name, course_name))
            return
        captcha_img = course_tr.find_elements_by_xpath("/td[0]/img")

        if len(captcha_img) == 0:
            print("此堂課目前已選滿")
            return
        captcha_arr = cv2.imdecode(np.fromstring(captcha_img.screenshot_as_png, np.uint8), 1)
        answer = self._rec_captcha(captcha_arr)
        answer_input = course_tr.find_element_by_xpath("/td[1]/input")
        answer_input.sendKeys(answer)
        submit_bt = course_tr.find_element_by_xpath("/td[2]/input")
        submit_bt.click()

    def _rec_captcha(self, captcha_arr):
        answer = None
        mask = (captcha_arr < 110).any(axis=-1)
        masked = cv2.bitwise_and(captcha_arr, captcha_arr, mask=mask.astype(np.uint8))
        threshed = cv2.threshold(masked, 0, 255, cv2.THRESH_BINARY_INV)
        return answer




