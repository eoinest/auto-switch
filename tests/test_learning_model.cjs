const assert = require('node:assert/strict');
const model = require('../learn/model.js');

// All combinations: source presence, master position and requested motor power.
for (const battery of [false, true]) for (const usb of [false, true]) {
  for (const master of [false, true]) for (const request of [false, true]) {
    const p = model.power({ battery, usb, master, request });
    assert.equal(p.pico, usb || (battery && master));
    assert.equal(p.servo, battery && master && request);
    assert.equal(p.control, p.pico && request);
    assert.equal(p.chipV, p.pico ? 3.3 : 0);
  }
}
const usbOnly = model.power({battery:false, usb:true, master:true, request:true});
assert.equal(usbOnly.control, true);
assert.equal(usbOnly.servo, false); // GPIO enable cannot create a motor supply.
assert.deepEqual(model.ohm(5, 1000), {amps:0.005, watts:0.025});
assert.ok(model.ohm(6, 100).watts > 0.25);
assert.throws(() => model.ohm(5,0), RangeError);
const divider = model.divider(4.8,100,47);
assert.ok(Math.abs(divider.volts - 1.5346938775510204) < 1e-12);
assert.ok(Math.abs(divider.microamps - 32.6530612244898) < 1e-10);
assert.equal(divider.safeNominal,true);
assert.equal(model.divider(6.4,10,200).safeNominal,false);
assert.throws(() => model.divider(Infinity,100,47), RangeError);
const defaults={capacityMah:1900,sleepMa:10,wakeMa:80,wakeSeconds:3,intervalSeconds:60,actions:20,servoMa:500,actionSeconds:1};
const energy=model.energy(defaults);
assert.ok(energy.days > 3.3 && energy.days < 3.5);
assert.equal(energy.nominalWh,9.12);
assert.equal(model.energy({...defaults,capacityMah:0}).days,0);
assert.ok(model.energy({...defaults,intervalSeconds:300}).days>energy.days);
assert.throws(()=>model.energy({...defaults,intervalSeconds:0}),RangeError);
console.log('Learning model: 16 power states, units, ADC limits and energy assumptions passed.');

const cap=model.capacitor(470,500,1);
assert.ok(Math.abs(cap.volts - (5 - 0.5 * 0.001 / 0.000470)) < 1e-12);
assert.equal(model.capacitor(470,500,10).volts,0);
assert.equal(model.capacitor(470,0,10).volts,5);
assert.throws(()=>model.capacitor(0,500,1),RangeError);
console.log('Capacitor units and depletion limits passed.');
