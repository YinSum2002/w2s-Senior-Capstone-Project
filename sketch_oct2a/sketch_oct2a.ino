const int trigPin = 9;  // Trig pin connected to Digital 9
const int echoPin = 10; // Echo pin connected to Digital 10
long duration;
int distance;

void setup() {
  // Set trigPin as output and echoPin as input
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600); // Start serial communication
}

void loop() {
  // Clear the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Set the trigPin HIGH for 10 microseconds to send a pulse
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read the echoPin, returns the duration (time) of the pulse in microseconds
  duration = pulseIn(echoPin, HIGH);

  // Calculate the distance (speed of sound is 34300 cm/s)
  distance = duration * 0.034 / 2;

  // Print the distance to the Serial Monitor
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  delay(500); // Wait before the next measurement
}
