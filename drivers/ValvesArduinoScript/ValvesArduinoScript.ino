
const int stateStart = 13;
const int stateV1 = 2;
const int stateV2 = 3;
const int stateV3 = 4;
const int stateV4 = 5;
const int stateV5 = 6;
void setup() {
  pinMode(stateStart, OUTPUT);
  pinMode(stateV1, OUTPUT);
  pinMode(stateV2, OUTPUT);
  pinMode(stateV3, OUTPUT);
  pinMode(stateV4, OUTPUT);
  pinMode(stateV5, OUTPUT);
  Serial.begin(9600);
}
void loop() { // if there's any serial available, read it:
  while (Serial.available() > 0) { //
    int start = Serial.parseInt();
    int v1 = Serial.parseInt();
    int v2 = Serial.parseInt();
    int v3 = Serial.parseInt();
    int v4 = Serial.parseInt();
    int v5 = Serial.parseInt();
    if (Serial.read() == '\n') {
      if(start==0) digitalWrite(stateStart, LOW); 
      else digitalWrite(stateStart, HIGH);
      if(v1==0) digitalWrite(stateV1, LOW);
      else digitalWrite(stateV1, HIGH);
      if(v2==0) digitalWrite(stateV2, LOW);
      else digitalWrite(stateV2, HIGH);
      if(v3==0) digitalWrite(stateV3, LOW);
      else digitalWrite(stateV3, HIGH);
      if(v4==0) digitalWrite(stateV4, LOW);
      else digitalWrite(stateV4, HIGH);
      if(v5==0) digitalWrite(stateV5, LOW);
      else digitalWrite(stateV5, HIGH);
    }
  }
}
