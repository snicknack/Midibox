# Farnell vs RS pricing

- ChatGPT conversation id: 68e8fb03-65e8-8332-9c93-cd12c3073c30
- Created: 2025-10-10 12:24
- Updated: 2025-10-10 12:26
- Project: Midibox raspberry pi
- Messages: 9

## User · 2025-10-10 12:24

[file: 22E519BF-4D14-4B07-A265-EFD0C8386CCD.jpeg (file_00000000edf462469e916784f81e2b3e)]

[image file_00000000edf462469e916784f81e2b3e 708x1536]
Where’s best place to buy one of these

## Tool (file_search) · 2025-10-10 12:24

> MidiBox Design Overview



Two Long Throw Faders for CC 



Transport Control via the MPR121 capacitive Touch

	Start, Stop, Rec, Jog L, Jog R, Loop, 



Pitch and Mod Wheel 



Fatar Midi Keyboard

	Aftertouch

	Velocity

	88 Keys



Touch Screen FT6236 and 

	

	Page 1

	Midi Transpose

	Midi Octave up/down

	Display Chords Played 

	Display 4 touch encoder parameters



	Page 2 - Arpeggiator

	Scale Major minor etc.

	Up/Down/Chord



	Page 3 - 2 Faders and 4 touch sensitive encoders Setup page

	Allow Change cc out of 2 faders

	Assign Touch sensitive encoders to internal functions such as midi transpose octave jump

	Or assign touch encoders to cc.



	Page 4 - Select USB Midi Out (for devices on USB-A ports



USB Midi out 

	USB-A allows class compliant midi devices such as synthesizers

	USB-C Allows connection to Class compliant Hosts such as OSX (gadget)





Other features

	Swipe functions 

	UI Design using a library such as Ktinter or Kivy, PyQt and PySide

	

Optional

RGB Leds available for suggestionsas previously tested

Buttons available for suggestions

	

	

Code Requirements



Skeleton Main.py - Not Bulky and full of code

Multiple Files/Modules for each Requirement (gestures, UI, Midi USB-C, Midi USB-A, Midi Scales CC and Transport functions.

Allows for Updates and my learning.

(When Project is complete) = Boot direct into Program with Boot Screen and no need for Pi OS interaction.













Hardware Equipment 



PI 4

Ft6236 3.2”TFT SPI  TouchScreen 240 x 320

MPR121 Break out (adafruit)

Midi and Pitch Wheels (analogue)

4 Smooth Encoders with Capacitive functionality and Clickable

Capacitive Pads for Transport Functions Not Purchased yet (make recommendations)

3D Printer for Case

Will need to create a 2M cable going from the FATAR Keyboard to my Midi Box

## Tool (file_search) · 2025-10-10 12:24

All the files uploaded by the user have been fully loaded. Searching won't provide additional information.

## Assistant · 2025-10-10 12:24

It depends a bit on how fast you need it, how much you’re willing to pay for shipping, and whether you want exactly that “Retex 33020112” model or something similar. Here are some good options + tips:

---

## ✅ Ready-to-buy options (or equivalents)

Here are some sloped desktop enclosures and similar alternatives you can order now:  
products{"selections":[["turn0product1","Retex Black Sloped Desktop Enclosure 268×185×78"],["turn0product0","Retex Grey Sloped Desktop Enclosure 268×185×78"],["turn0product4","Evatron IP65 ABS Sloping Desktop Enclosure"],["turn0product3","Hammond Sloped Enclosure 518-0910"],["turn0product11","OKW DATEC Sloped Desktop Enclosure"],["turn0product5","Hammond 1456PG4 Sloped Enclosure"],["turn0product7","Hammond 1456PK4 Sloped Enclosure"],["turn0product6","Hammond Sloped Enclosure 500-0940"]],"tags":["exact size (black)","exact size (grey)","weatherproof ABS","compact model","premium brand","larger size variant","another size variant","mid-size"]}  

Here are a few highlights:

- **product_entity["turn0product1","Retex Black Sloped Desktop Enclosure 268×185×78"]** — closest match to your photo (the same model)  
- **product_entity["turn0product0","Retex Grey Sloped Desktop Enclosure 268×185×78"]** — same dimensions, different color  
- **product_entity["turn0product4","Evatron IP65 ABS Sloping Desktop Enclosure"]** — good if you want more dust/water protection  
- **product_entity["turn0product3","Hammond Sloped Enclosure 518-0910"]** — a common brand, likely easier to source  
- **product_entity["turn0product11","OKW DATEC Sloped Desktop Enclosure"]** — premium finish and build  
- **product_entity["turn0product5","Hammond 1456PG4 Sloped Enclosure"]**  
- **product_entity["turn0product7","Hammond 1456PK4 Sloped Enclosure"]**  
- **product_entity["turn0product6","Hammond Sloped Enclosure 500-0940"]**  

You can click through those (via their merchant links) to see pricing and availability in the UK.

---

## 🏬 Specialist suppliers and UK sources

If you prefer to stay local or order from trusted UK electronics suppliers:

- **CPC / Farnell** (UK) stock the exact “**RETEX 33020112 Black Sloped Desktop Enclosure**” (268×185×78 mm). citeturn0search0turn0search2  
- **TME** also list the same model (or a close variant) under their “desktop enclosure” category. citeturn0search3turn0search4  
- You can check other UK electronics parts houses like RS Components, Mouser UK, Rapid Electronics, etc.
- On general marketplaces, I saw one listing on Amazon UK for the “Sloped Console 268×78×185 mm” listing that matches “33020112”. citeturn0search1  

---

## 🎯 My recommendation

If you want exactly the same model with minimal fuss, ordering **Retex 33020112** from CPC / Farnell is your safest bet (UK supplier, decent shipping).  
If you want better protection (IP rating) or different aesthetics, choose one of the alternative enclosures above that match your needed internal dimensions.

If you like, I can check what UK stock is available *right now* and send you direct purchase links. Would you prefer I find ones available for delivery to your address?

## User · 2025-10-10 12:26

Which is cheaper farnell or rs in general for hobbyists 

## Assistant · 2025-10-10 12:26

Good question — and it’s one that a lot of UK makers and engineers run into 👇  

Here’s a quick, honest comparison:

---

### 🟢 **CPC / Farnell**
*(CPC is Farnell’s hobbyist-facing arm — same stock, lower prices on small quantities)*

**Pros**
- **Cheaper for single units** and small orders — CPC specifically targets makers, hobbyists, and schools.  
- **Low or no minimum order value.**  
- **Free delivery** on orders over ~£17.50 (ex VAT).  
- Stocks **RETEX**, **Hammond**, **Evatron**, etc.  
- Often has **clearance and bundle deals** on enclosures, power supplies, cables, etc.  
- Excellent for **Raspberry Pi, Arduino, sensors, etc.**

**Cons**
- Sometimes **longer lead times** for parts shipped from Farnell’s EU warehouse.  
- Website search isn’t as refined as RS’s.  
- **Limited technical documentation** compared to RS.

💷 **Typical pricing:** about 5–15% cheaper than RS for the same small quantities.

---

### 🔵 **RS Components (RS Online / RS PRO)**
**Pros**
- **Extremely reliable** and fast (next-day delivery standard).  
- Massive catalogue — almost every industrial part imaginable.  
- Great **technical datasheets** and CAD models.  
- **Trade quality**, often UK-stocked.  

**Cons**
- **Expensive for small orders** — they assume you’re a business account.  
- Some parts have **minimum order quantities**.  
- Free delivery often only above **£30–£50**, depending on account type.  
- “RS PRO” branded stuff is sometimes re-badged generic gear at a premium.

💷 **Typical pricing:** around 10–25% higher than CPC/Farnell for single-unit purchases.

---

### ⚙️ **Summary Table**

| Supplier | Best For | Hobbyist Price | Delivery | Notes |
|-----------|-----------|----------------|-----------|-------|
| **CPC (Farnell)** | Makers, Pi projects, low quantity | ⭐ Usually cheapest | Free >£17.50 | Same stock as Farnell but cheaper |
| **Farnell Direct** | Pro engineers, bulk orders | Medium | Free >£30 | More industrial focus |
| **RS Components** | Industrial / Pro buyers | ❌ Pricier | Fast (next day) | Excellent service & datasheets |

---

### 🧠 Recommendation for you
For **Midibox builds and one-off enclosures**, **CPC** is your best bet — cheaper per unit, same quality, and low minimums.  
If you ever move to **batch production (10–20 units)**, Farnell’s bulk pricing or RS’s business account might then make sense.

---

Would you like me to check current CPC vs RS prices **for that exact RETEX 33020112** right now? I can pull the live difference including VAT and delivery.

