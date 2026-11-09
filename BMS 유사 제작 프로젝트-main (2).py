# ============================================================
# 유사 배터리 관리 시스템(BMS)
# TMP36 온도센서로 배터리 온도 측정 -> 기준온도 넘으면 모터(냉각팬) 작동
# -> OLED에 온도/상태 문자 표시
#
# [배선]
#   TEMP_PIN(기본 P1) : TMP36의 OUT 핀 연결
#                        TMP36 VCC -> 마이크로비트 3V, GND -> GND, OUT -> P1
#   MOTOR_PIN(기본 P2): 모터(프로펠러) 브릭 연결 (확장보드 P2 포트)
#   OLED             : SCL -> P19, SDA -> P20, VCC -> 3V, GND -> GND
#                       (확장보드에 I2C 라고 표시된 포트가 있다면 그 포트 사용)
#
# [필요 파일] 아래 3개 파일을 모두 마이크로비트에 함께 업로드해야 합니다.
#   - main.py (이 파일)
#   - ssd1306.py
#   - ssd1306_text.py
#
# [주의] OLED 글자는 마이크로비트 내장 폰트를 사용하므로 영문/숫자만 표시됩니다.
# ============================================================

from microbit import *
from ssd1306 import initialize, clear_oled
from ssd1306_text import add_text

# ---------------- 포트 설정 ----------------
TEMP_PIN = pin1     # TMP36 OUT
MOTOR_PIN = pin2    # 모터(프로펠러) 브릭

# ---------------- 사용자 설정값 ----------------
FAN_ON_TEMP = 28     # 이 온도(°C) 이상이면 팬 가동
DANGER_TEMP = 40     # 이 온도 이상이면 위험 경고
CHECK_INTERVAL_MS = 500


def read_temp_c():
    """TMP36 출력 전압을 섭씨 온도로 변환 (10mV/°C, 0°C=0.5V)"""
    raw = TEMP_PIN.read_analog()          # 0~1023
    voltage = raw / 1023 * 3.3
    return (voltage - 0.5) * 100


def set_fan(on):
    """모터 브릭 ON/OFF. 속도조절(PWM) 되는 브릭이면 아래 줄로 교체 가능:
       MOTOR_PIN.write_analog(1023 if on else 0)"""
    MOTOR_PIN.write_digital(1 if on else 0)


initialize()
clear_oled()

while True:
    t = read_temp_c()

    if t >= DANGER_TEMP:
        set_fan(True)
        state = "DANGER"
        icon = Image.SKULL
    elif t >= FAN_ON_TEMP:
        set_fan(True)
        state = "COOLING"
        icon = Image.YES
    else:
        set_fan(False)
        state = "NORMAL"
        icon = Image.HAPPY

    # OLED 표시 (영문/숫자만 가능, 한 줄 최대 12자)
    clear_oled()
    add_text(0, 0, "BMS MONITOR", 0)
    add_text(0, 1, "TEMP:" + str(int(t)) + "C", 0)
    add_text(0, 2, "STATE:" + state, 1)

    # LED 매트릭스에도 상태 아이콘 표시
    display.show(icon)

    # 시리얼로 값 확인 (Mu 에디터, 플로터 등에서 모니터링 가능)
    print("Temp:", t, "State:", state)

    sleep(CHECK_INTERVAL_MS)
