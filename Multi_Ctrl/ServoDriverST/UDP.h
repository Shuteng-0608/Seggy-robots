#include <WiFi.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <stdint.h>

typedef char s8;
typedef unsigned char u8; 
typedef unsigned short u16; 
typedef short s16;
typedef unsigned long u32;  
typedef long s32;

WiFiUDP Udp;
const int udpPort = 12345; // Port number for UDP communication

void setRGBColor(byte r, byte g, byte b); // Control all LED light on board

// Set board as STA
// Connect to know wifi (Target wifi needs to satisfy - "2.4GHz" && "WPA2")
void wifiConnect(){
  WiFi.begin(STA_SSID, STA_PWD);

  while(WiFi.status() != WL_CONNECTED){
    delay(1000);
    Serial.print(".");
  }
  Serial.println("Connected to WiFi");
}


// UDP init
void udpInit(){
  Udp.begin(udpPort);
  Serial.print("UDP listening on port ");
  Serial.println(udpPort);
}


// Handle coming msg
void handleUdp(){
  int packetSize = Udp.parsePacket(); // Check is there any msg coming
  if(packetSize){
    char buffer[255];
    int len = Udp.read(buffer, 255); // Read the coming msg
    if (len > 0) {
      buffer[len] = 0; // Null-terminate the string
    }
    String message = String(buffer);
    Serial.println("Received: " + message);

    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, message);
    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      return;
    }

    const char* cmd = doc["Cmd"];  
    
    if(strcmp(cmd, "RGB") == 0){
      u8 id = doc["ID"];
      byte r = doc["R"];
      byte g = doc["G"];
      byte b = doc["B"];
      setRGBColor(r, g, b);
    }

    else if(strcmp(cmd, "WritePosEx") == 0){
      u8 id = doc["ID"];
      s16 pos = doc["pos"];
      u16 vel = doc["vel"];
      u8 acc = doc["acc"];
      // WritePosEx(u8 ID, s16 Position, u16 Speed, u8 ACC = 0);
      st.WritePosEx(id, pos, vel, acc);
    }

    else if(strcmp(cmd, "RegWritePosEx") == 0){
      u8 id = doc["ID"];
      s16 pos = doc["pos"];
      u16 vel = doc["vel"];
      u8 acc = doc["acc"];
      // RegWritePosEx(u8 ID, s16 Position, u16 Speed, u8 ACC = 0);
      st.RegWritePosEx(id, pos, vel, acc);
    }

    else if(strcmp(cmd, "SyncWritePosEx") == 0){
      JsonArray ID_list = doc["ID_list"];
      uint8_t IDNum = doc["IDNum"];
      JsonArray pos_list = doc["pos_list"];
      JsonArray vel_list = doc["vel_list"];
      JsonArray acc_list = doc["acc_list"];
      
      uint8_t IDArray[ID_list.size()];
      int16_t posArray[pos_list.size()];
      uint16_t velArray[vel_list.size()];
      uint8_t accArray[acc_list.size()];
      
      for (int i = 0; i < ID_list.size(); i++) IDArray[i] = ID_list[i].as<u8>();
      for (int i = 0; i < pos_list.size(); i++) posArray[i] = pos_list[i].as<s16>();  
      for (int i = 0; i < vel_list.size(); i++) velArray[i] = vel_list[i].as<u16>();  
      for (int i = 0; i < acc_list.size(); i++) accArray[i] = acc_list[i].as<u8>();   
      // SyncWritePosEx(u8 ID[], u8 IDN, s16 Position[], u16 Speed[], u8 ACC[]);
      st.SyncWritePosEx(IDArray, IDNum, posArray, velArray, accArray);
    }

    
    else if(strcmp(cmd, "Position+") == 0){
      u8 id = doc["ID"];
      // WritePosEx(u8 ID, s16 Position, u16 Speed, u8 ACC = 0);
      st.WritePosEx(id, ServoDigitalRange_ST - 1, activeServoSpeed, ServoInitACC_ST);
    }
    
    else if(strcmp(cmd, "Position-") == 0){
      u8 id = doc["ID"];
      // WritePosEx(u8 ID, s16 Position, u16 Speed, u8 ACC = 0);
      st.WritePosEx(id, 0, activeServoSpeed, ServoInitACC_ST);
    }  
  }
}

void setRGBColor(byte r, byte g, byte b) {
  // Implement RGB LED control
  setSingleLED(0, matrix.Color(r, g, b));
  setSingleLED(1, matrix.Color(r, g, b));
}
