// File: dyno.ino

const int inputPin = 7;
volatile bool eventReady = false;
volatile unsigned long lastMicros = 0;
const unsigned long debounceThreshold = 0;  // 700 ms debounce no debounce filter, but pullses should not be less than 700us apart
volatile unsigned long deltaMicros = 0;

void setup() {
  pinMode(inputPin, INPUT_PULLUP);  // Detect pull-to-ground
  Serial.begin(115200);
  attachInterrupt(digitalPinToInterrupt(inputPin), onFallingEdge, FALLING);
  delay(2000); // Allow time for Serial Monitor to open
}

void loop() {
  if (eventReady) {
    noInterrupts();
    unsigned long delta = deltaMicros;
    eventReady = false;
    interrupts();
    Serial.println(delta);  // Send delta to Python
  }
}

void onFallingEdge() {
  unsigned long now = micros();
  if (now - lastMicros >= debounceThreshold) {
    deltaMicros = now - lastMicros;
    eventReady = true;
    lastMicros = now;
  }
}
