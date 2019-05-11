/*                                                                            //

            The HSB to RGB converter was made by Julio Terra
                      LINK TO THE ORIGINAL GITHUB:
                  https://github.com/julioterra/HSB_Color
*/                                                                            //

#define RED_LED 3
#define BLUE_LED 6
#define GREEN_LED 9

#include <math.h>
#include "HSBColor.h"

void setColor(int r, int g, int b) {
    analogWrite(RED_LED, r);
    analogWrite(GREEN_LED, g);
    analogWrite(BLUE_LED, b);
}

int cc = 0;
void cycle() {
    if (cc > 359) {
        cc = 1;
    }
    int * color;
    H2R_HSBtoRGB(cc, 100, 50, color);
    setColor(color[0], color[1], color[2]);
    cc++;
}

void setup() {
    Serial.begin(9600);
    pinMode(RED_LED, OUTPUT);
    pinMode(GREEN_LED, OUTPUT);
    pinMode(BLUE_LED, OUTPUT);
}

long last = millis();
long clear = millis();
void loop() {
    if (Serial.available() > 0) {
        setColor(0, 0, 0);
        clear = millis();
        byte input = Serial.read();
        int ran = random(30, 320);
        cc = cc + ran;
    }
    if ((millis() - last) > 10) {
        if (clear != 0) {
            if ((millis() - clear) > 40) {
                clear = 0;
                cycle();
            }
        } else {
            cycle();
        }
        last = millis();
    }
}
