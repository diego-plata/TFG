#include <WiFi.h>
#include <PubSubClient.h>
#include <DHTesp.h>

#define FLOW_SENSOR_PIN 35
#define RELAY_PIN 2
#define DHT_PIN 25
#define DHT_TYPE DHT22

const char* ssid = "PLATA";
const char* password = "88888888";

const char* mqtt_server = "192.168.1.58";
const char* mqtt_topic_data = "sensor/datos";
const char* mqtt_topic_start = "sensor/arranque";

WiFiClient espClient;
PubSubClient client(espClient);
DHTesp dht;

unsigned long totalPulses;

const float pulsesToVolume = 0.30811;
int targetVolume = 0;
String device_id;

int wateringState = 0; // 0: nada, 1: riego, 2: fin riego
unsigned long wateringStartMillis;
unsigned long pulseCountStart;
float movedVolume = 0;

void countPulse() {
    totalPulses++;
}

void callback(char* topic, byte* payload, unsigned int length) {
    char message[length + 1];
    memcpy(message, payload, length);
    message[length] = '\0';

    if (String(topic) == "/sensor/" + device_id) {
        targetVolume = atoi(message);
        wateringState = 1; // Cambio a estado de riego
        wateringStartMillis = millis();
        pulseCountStart = totalPulses;
    }
}

void setup() {
    Serial.begin(115200);
    dht.setup(DHT_PIN, DHTesp::DHT22);

    pinMode(FLOW_SENSOR_PIN, INPUT);
    digitalWrite(FLOW_SENSOR_PIN, HIGH);

    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Conectando a la red WiFi...");
    }
    
    Serial.println("Conectado a la red WiFi");
    // Generar un ID aleatorio de 9 cifras
    randomSeed(analogRead(0)); //  números aleatorios
    device_id = String(random(100000000, 999999999));

    client.setServer(mqtt_server, 1883);
    client.setCallback(callback);
    
    while (!client.connected()) {
        Serial.println("Conectando al broker MQTT...");
        if (client.connect(device_id.c_str())) {
            Serial.println("Conectado al broker MQTT");
            String topic = "/sensor/" + device_id;
            client.subscribe(topic.c_str());
        } else {
            Serial.print("Fallo al conectar al broker MQTT, rc=");
            Serial.print(client.state());
            Serial.println(" Intentando de nuevo en 5 segundos...");
            delay(5000);
        }
    }

    char start_msg[50];
    snprintf(start_msg, 50, "{\"device_id\":\"%s\",\"ip\":\"%s\"}", device_id.c_str(), WiFi.localIP().toString().c_str());
    client.publish(mqtt_topic_start, start_msg);

    attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), countPulse, RISING);
}

void loop() {
    static unsigned long lastSendTime = 0;
    static unsigned long lastWateringCheck = 0;

    if (millis() - lastSendTime > 10000) {
        float humidity = dht.getHumidity();
        float temperature = dht.getTemperature();
        int soilMoistureValue = analogRead(34);

        char msg[200];
        snprintf(msg, 200, "{\"device_id\":\"%s\",\"humidity\":%.2f,\"temperature\":%.2f,\"soil_moisture\":%d}", device_id.c_str(), humidity, temperature, soilMoistureValue);
        client.publish(mqtt_topic_data, msg);

        lastSendTime = millis();
    }

    switch (wateringState) {
        case 0: 
            // No hacer nada
            break;
        case 1: // reganding
            if (millis() - lastWateringCheck > 500) { // Chequea cada 500 ms
                digitalWrite(RELAY_PIN, HIGH);
                delay(1000); // poco a poco pq la tierra traga lento
                digitalWrite(RELAY_PIN, LOW);

                movedVolume = (totalPulses - pulseCountStart) * pulsesToVolume;
                Serial.print("Volumen movido: ");
                Serial.print(movedVolume);
                Serial.println(" ml");

                if (movedVolume >= targetVolume) {
                    wateringState = 2; // Cambio a estado de riego completado
                }
                
                lastWateringCheck = millis();
            }
            break;
        case 2: // regado
            wateringState = 0; // Volver al estado IDLE
            Serial.println("Riego completado.");
            break;
    }

    client.loop();
}
