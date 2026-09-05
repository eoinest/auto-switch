/* Small explicit teaching models, independent of DOM or hardware. */
(function (root) {
  "use strict";
  function finite(value, minimum, name) {
    if (!Number.isFinite(value) || value < minimum) throw new RangeError(name + " is outside the model's range");
    return value;
  }
  const api = {
    power({ battery, usb, master, request }) {
      const regulated = Boolean(battery && master);
      const pico = Boolean(regulated || usb);
      return { battery: Boolean(battery), usb: Boolean(usb), regulated, pico,
        control: Boolean(pico && request), servo: Boolean(regulated && pico && request),
        vsysExampleV: pico ? 4.7 : 0, chipV: pico ? 3.3 : 0,
        servoV: regulated && request ? 5 : 0 };
    },
    ohm(volts, ohms) {
      finite(volts, 0, "Voltage"); finite(ohms, Number.MIN_VALUE, "Resistance");
      const amps = volts / ohms;
      return { amps, watts: volts * amps };
    },
    divider(pack, topK, bottomK) {
      finite(pack, 0, "Pack voltage"); finite(topK, Number.MIN_VALUE, "Top resistance"); finite(bottomK, Number.MIN_VALUE, "Bottom resistance");
      const volts = pack * bottomK / (topK + bottomK);
      return { volts, microamps: pack / ((topK + bottomK) * 1000) * 1e6,
        ideal12bit: Math.round(Math.min(1, volts / 3.3) * 4095),
        safeNominal: volts <= 3.3, scale: (topK + bottomK) / bottomK };
    },
    capacitor(capUf, currentMa, durationMs, initialV = 5) {
      finite(capUf, Number.MIN_VALUE, "Capacitance"); finite(currentMa, 0, "Current");
      finite(durationMs, 0, "Duration"); finite(initialV, 0, "Initial voltage");
      const farads = capUf / 1e6, amps = currentMa / 1000, seconds = durationMs / 1000;
      const drop = amps * seconds / farads;
      return { volts: Math.max(0, initialV - drop), drop: Math.min(initialV, drop),
        depleted: drop >= initialV, initialJoules: 0.5 * farads * initialV * initialV };
    },
    energy({ capacityMah, sleepMa, wakeMa, wakeSeconds, intervalSeconds, actions, servoMa, actionSeconds }) {
      [capacityMah, sleepMa, wakeMa, wakeSeconds, actions, servoMa, actionSeconds].forEach(v => finite(v, 0, "Energy input"));
      finite(intervalSeconds, Number.MIN_VALUE, "Poll interval");
      const awake = Math.min(1, wakeSeconds / intervalSeconds + actions * actionSeconds / 86400);
      const logicMa = sleepMa * (1 - awake) + wakeMa * awake;
      const nominalWh = 4.8 * capacityMah / 1000;
      const accessibleWh = nominalWh * 0.8;
      const logicWhDay = 5 * logicMa / 1000 * 24 / 0.85;
      const servoWhDay = 5 * servoMa / 1000 * actions * actionSeconds / 3600 / 0.85;
      const parasiticWhDay = 4.8 * 2.05 / 1000 * 24;
      const totalWhDay = logicWhDay + servoWhDay + parasiticWhDay;
      return { logicMa, nominalWh, accessibleWh, logicWhDay, servoWhDay, parasiticWhDay,
        totalWhDay, days: accessibleWh / totalWhDay };
    }
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.CircuitModel = api;
})(typeof window !== "undefined" ? window : globalThis);
