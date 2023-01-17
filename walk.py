
    @staticmethod

    def walk(self, stats, champion, x, y, game_time):

        attack_speed_cap = OrbWalker.get_attack_speed_cap(stats, champion, game_time)

        if x is not None and y is not None and self.can_attack_time < game_time:
            stored_x, stored_y = mouse.get_position()


            mouse.move(int(x), int(y))
            mouse.right_click()
            time.sleep(0.01)
            game_time = find_game_time(self.mem)
            attack_speed_base, attack_speed_ratio = stats.get_attack_speed(champion.name)
            windup_percent, windup_modifier = stats.get_windup(champion.name)
            self.can_attack_time = game_time + OrbWalker.get_attack_time(champion, attack_speed_base, attack_speed_ratio, attack_speed_cap)
            self.can_move_time = game_time + OrbWalker.get_windup_time(champion, attack_speed_base, attack_speed_ratio, windup_percent, windup_modifier, attack_speed_cap)
            mouse.move(stored_x, stored_y)
        elif self.can_move_time < game_time:
            mouse.right_click()
            MOVE_CLICK_DELAY = 0.05
            self.can_move_time = game_time + MOVE_CLICK_DELAY


class testing:
    @staticmethod
    def findAndMove2():
        location = pyautogui.locateCenterOnScreen(
            "enemyIconLvl1.png", region=(xSearchBase, ySearchBase, xSearchSize, ySearchSize), confidence=confidence)
        print(location)

        m = pm.mouse_position()

        try:
            print(int(location.x-m['x']))
            print(int(location.y-m['y']))
            pm.mouse_move(
                int(((location.x + 50) - m['x'])*2),
                int(((location.y + 150)-m['y'])*-2))

            pydirectinput.keyDown("j")
            pydirectinput.keyUp("j")

            pm.mouse_move(
                int((m['x']-(location.x + 50))*2),
                int((m['y']-(location.y + 150))*-2)
            )

            print("\a")

            time.sleep((1/attackSpeed) * attackWindPercentage)
            # print("windup : " + str((1/attackSpeed) * attackWindPercentage))

            # interval = (((1/attackSpeed) * (1-(attackWindPercentage*2)))/10)

            pydirectinput.keyDown("k")
            pydirectinput.keyUp("k")

            # print("next : " + str((1/attackSpeed) * (1-(attackWindPercentage*2))))

            time.sleep((1/attackSpeed) * (1-(attackWindPercentage*2)))