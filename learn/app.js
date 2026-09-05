(function () {
  "use strict";
  const data = window.AUTO_SWITCH_LEARN;
  const M = window.CircuitModel;
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const safeUrl = value => /^https?:\/\//.test(value || "") ? esc(value) : "#";
  if (!data || !M) {
    $("main").innerHTML = "<h1>Learning files are missing.</h1><p>Run <code>python3 tools/build_learning.py</code> from the repository, then reopen this page.</p>";
    return;
  }
  const course = data.course;
  const sources = Object.fromEntries(course.sources.map(s => [s.id, s]));
  const sourceLinks = ids => (ids || []).map(id => sources[id] ? `<a href="${safeUrl(sources[id].url)}" target="_blank" rel="noopener">${esc(sources[id].title)}</a>` : "").join(" · ");
  const paragraphs = value => String(value || "").split(/\n\s*\n/).map(p => `<p>${esc(p)}</p>`).join("");
  const storageKey = "auto-switch-learning-v1";
  let answers = {};
  try { const saved = JSON.parse(localStorage.getItem(storageKey) || "{}"); if (saved && typeof saved === "object" && !Array.isArray(saved)) answers = saved; } catch (_) { /* Learning works without storage. */ }
  function save() { try { localStorage.setItem(storageKey, JSON.stringify(answers)); } catch (_) { /* Private/file browser policies may disable persistence. */ } }
  const completed = lesson => lesson.quiz.every(q => answers[q.id] === q.answer_index);
  let currentLesson = course.lessons[0].id;
  let currentLab = "ohm";
  let supply = "battery";

  const parts = {
    BAT: ["Battery holder", "Four AA NiMH cells sit in the Pololu 1153 holder. Its built-in metal contacts and red/black leads collect their energy. Four cells in series add their voltages; their mAh capacity does not add."],
    F1: ["Fuse", "The fuse sits close to battery positive. It is a sacrificial part that opens after sufficient overcurrent for sufficient time. A 2 A time-delay rating is not an instant 2 A current limit."],
    RCY: ["Battery connector", "The mating prewired RCY plugs let you remove the battery holder without unsoldering wires. Check actual polarity and put recessed live contacts on the fused battery side."],
    MASTER: ["Battery master switch", "This Pololu 2810 removes the battery supply from BOTH the regulator and the voltage divider. With USB plugged in, switching the battery master off still leaves the Pico powered by USB."],
    REG: ["External 5 V regulator", "The battery voltage changes with charge and load. The Pololu S18V20F5 buck-boost converts it to a regulated 5 V rail. That rail splits: one branch feeds the Pico through D1; another feeds the servo gate. A higher voltage is not free energy; input current depends on power and efficiency."],
    D1: ["Our supply diode D1", "This is a bought 1N5819, separate from the diode already inside the Pico. Its anode connects to external 5 V and its striped cathode to VSYS. It lets external power reach the Pico while blocking USB-derived VSYS from feeding back into our 5 V motor rail."],
    PICO: ["Inside the Pico", "VSYS is physical pad 39, the input to the Pico's on-board regulator. That regulator makes 3.3 V for the chip and GPIO. VBUS is pad 40, connected to USB's 5 V. These are power connections, not GPIO39 or GPIO40. The headerless board has exactly the same named edge pads."],
    USB: ["USB power", "The cable brings nominal 5 V to VBUS. The Pico's existing on-board diode connects VBUS toward VSYS. USB alone powers the Pico in this design, but cannot power the separately diode-isolated servo branch."],
    GATE: ["Servo power gate", "This second Pololu 2810 carries the servo's supply current. Leave its physical slider OFF. GP15 supplies only a small 3.3 V control signal to ON; the motor's energy comes from the separate 5 V branch. A 100 kΩ pulldown keeps the enable low during reset."],
    SERVO0: ["First servo", "The servo needs three connections: switched 5 V, GND and its own PWM signal. GPIO16 sends pulse timing through a 1 kΩ resistor; it does not supply the motor's power. The controller presses, returns to neutral and removes servo supply power."],
    SERVO1: ["Second servo", "The optional second MG90S shares supply and ground but has its own GPIO17 signal and 1 kΩ series resistor. Omit both for a single-switch build. Firmware moves only one servo at a time."],
    ADC: ["Battery measurement", "A 100 kΩ / 47 kΩ divider reduces raw pack voltage to a level GP26 can measure. At 4.8 V it produces about 1.53 V. A 100 nF capacitor filters this node. Sensing regulated VSYS would hide most of the battery's decline."],
    GND: ["Common ground", "GND is both the chosen zero-volt reference and part of each complete current loop. It is not automatically Earth. Battery negative, Pico, regulator and servo grounds connect together. Route motor return directly to the power assembly rather than through the Pico."],
  };

  $("power-svg").innerHTML = data.diagrams.power;
  // The two independent SVG files may share definition IDs. Scope the embedded sheet.
  function scopedSvg(svg, prefix) {
    const xml = new DOMParser().parseFromString(svg, "image/svg+xml");
    const ids = Array.from(xml.querySelectorAll("[id]")).map(el => el.id);
    xml.querySelectorAll("*").forEach(el => {
      for (const attr of Array.from(el.attributes)) {
        let value = attr.value;
        if (attr.name === "id") value = prefix + value;
        else {
          value = value.replace(/url\(#([^)]*)\)/g, (_, id) => "url(#" + prefix + id + ")");
          if ((attr.name === "href" || attr.name === "xlink:href") && value.startsWith("#")) value = "#" + prefix + value.slice(1);
          if (attr.name === "aria-labelledby" || attr.name === "aria-describedby") value = value.split(/\s+/).map(id => ids.includes(id) ? prefix + id : id).join(" ");
        }
        el.setAttribute(attr.name, value);
      }
    });
    return new XMLSerializer().serializeToString(xml.documentElement);
  }
  $("wiring-svg").innerHTML = scopedSvg(data.diagrams.wiring, "sheet-");
  let mapZoom = 100;
  function zoomMap(value) {
    mapZoom = Math.max(100, Math.min(600, value));
    const frame = $("map-canvas");
    const fitWidth = Math.min(frame.clientWidth - 2, (frame.clientHeight - 2) * 2200 / 1400);
    if (fitWidth > 0) $("wiring-svg").style.width = fitWidth * mapZoom / 100 + "px";
    $("map-zoom").textContent = mapZoom + "%";
    $("map-out").disabled = mapZoom === 100;
    $("map-in").disabled = mapZoom === 600;
    if (mapZoom === 100) $("map-canvas").scrollTo(0, 0);
  }
  $("map-fit").onclick = () => zoomMap(100);
  $("map-out").onclick = () => zoomMap(mapZoom - 25);
  $("map-in").onclick = () => zoomMap(mapZoom + 25);
  $("map-fullscreen").onclick = async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await $("page-wiring").requestFullscreen();
    } catch (_) { $("map-zoom").textContent = "Use the full-size SVG link in this browser."; }
  };
  document.addEventListener("fullscreenchange", () => { $("map-fullscreen").textContent = document.fullscreenElement ? "Exit full screen" : "Full screen"; requestAnimationFrame(() => zoomMap(mapZoom)); });
  window.addEventListener("resize", () => zoomMap(mapZoom));
  zoomMap(100);
  $("bb-svg").innerHTML = scopedSvg(data.diagrams.breadboard, "bb-");
  let bbZoom=100;
  function zoomBreadboard(value) {
    bbZoom=Math.max(100,Math.min(600,value));
    const frame=$("bb-canvas"), width=Math.min(frame.clientWidth-2,(frame.clientHeight-2)*2150/1690);
    if(width>0)$("bb-svg").style.width=width*bbZoom/100+"px";
    $("bb-zoom").textContent=bbZoom+"%";$("bb-out").disabled=bbZoom===100;$("bb-in").disabled=bbZoom===600;
    if(bbZoom===100)frame.scrollTo(0,0);
  }
  $("bb-fit").onclick=()=>zoomBreadboard(100);$("bb-out").onclick=()=>zoomBreadboard(bbZoom-50);$("bb-in").onclick=()=>zoomBreadboard(bbZoom+50);
  $("bb-fullscreen").onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await $("page-breadboard").requestFullscreen();}catch(_){$("bb-zoom").textContent="Use the full-size layout link.";}};
  document.addEventListener("fullscreenchange",()=>{$("bb-fullscreen").textContent=document.fullscreenElement?"Exit full screen":"Full screen";requestAnimationFrame(()=>zoomBreadboard(bbZoom));});
  window.addEventListener("resize",()=>zoomBreadboard(bbZoom));
  $("bb-step").insertAdjacentHTML("beforeend",data.breadboard.steps.map(s=>`<option value="${s.id}">${s.id}. ${esc(s.title)}</option>`).join(""));
  function renderBreadboard() {
    const gangs=Number($("bb-gangs").value);
    $("bb-step").querySelector('option[value="5"]').disabled=gangs===1;
    if(gangs===1&&$("bb-step").value==="5")$("bb-step").value="0";
    const step=Number($("bb-step").value),info=data.breadboard.steps.find(s=>s.id===step);
    $("bb-instruction").innerHTML=info?`<h3>${esc(info.title)}</h3><p>${esc(info.text)}</p>`:'<h3>Start with all power disconnected.</h3><p>Choose a numbered step to highlight just those parts and cables. Place the board with USB up; confirm its row labels. The guide includes unpowered continuity checks and voltage checks with the Pico removed before first power-up.</p>';
    $("bb-svg").querySelectorAll("[data-bb-step]").forEach(el=>{const n=Number(el.dataset.bbStep);el.classList.toggle("bb-dim",(step!==0&&step!==6&&n!==step)||(gangs===1&&n===5));});
    const rows=data.breadboard_rows.filter(r=>(gangs===2||r.optional!=="True")&&(step===0||step===6||Number(r.step)===step));
    $("bb-table").innerHTML=rows.map(r=>`<tr><td><strong>${esc(r.id)}</strong><small>${esc(r.value)}</small></td><td>${esc(r.start)}</td><td>${esc(r.end)}</td><td>${esc(r.note)}</td></tr>`).join("");
  }
  $("bb-step").onchange=renderBreadboard;$("bb-gangs").onchange=renderBreadboard;
  $("bb-sources").innerHTML=data.breadboard.sources.map(s=>`<p><a href="${safeUrl(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a></p>`).join("");
  renderBreadboard();
  $("inspect-part").innerHTML = Object.entries(parts).map(([id, p]) => `<option value="${id}">${esc(p[0])}</option>`).join("");
  function inspectPart(id) {
    if (!parts[id]) return;
    $("inspect-part").value = id;
    $("part-detail").innerHTML = `<p><strong>${esc(parts[id][0])}.</strong> ${esc(parts[id][1])}</p>`;
  }
  $("inspect-part").addEventListener("change", e => inspectPart(e.target.value));
  $("power-svg").addEventListener("click", e => { const part = e.target.closest("[data-part]"); if (part) inspectPart(part.dataset.part); });
  inspectPart("PICO");

  function updatePower() {
    const p = M.power({battery: supply === "battery" || supply === "both", usb: supply === "usb" || supply === "both", master: $("master-on").checked, request: $("servo-request").checked});
    const states = {"path-battery":p.battery,"path-pack-sw":p.regulated,"path-regulated":p.regulated,"path-pico-external":p.regulated,"path-usb":p.usb,"path-vsys":p.pico,"path-3v3":p.pico,"path-motor-input":p.regulated,"path-motor-output":p.servo,"path-ground":true,"path-control":p.control,"path-pwm":p.servo,"path-adc":p.regulated};
    for (const [id, on] of Object.entries(states)) {
      const node = $("power-svg").querySelector("#" + id);
      if (node) node.classList.toggle("is-off", !on);
    }
    $("pico-voltage").textContent = p.pico ? "3.3 V · awake" : "0 V · off";
    $("servo-voltage").textContent = p.servo ? "5 V · enabled" : "0 V · off";
    let explanation;
    if (p.regulated && p.usb) explanation = "Both paths can supply VSYS. The higher voltage after its diode normally supplies it; sharing is possible when close. There is no guaranteed USB priority. The servo still depends on the battery branch.";
    else if (p.regulated) explanation = "The batteries feed our 5 V regulator. D1 passes that supply to VSYS; the Pico's own regulator then powers its chip at 3.3 V.";
    else if (p.usb) explanation = p.control ? "USB powers the Pico and GP15 can request power, but the motor's 5 V source is absent. The servo remains off." : "USB reaches VBUS, then the on-board diode, VSYS and the Pico's 3.3 V regulator. Our external D1 blocks this supply from powering the servos or batteries.";
    else explanation = "No supply reaches VSYS. The Pico and servos are off. A checked servo request cannot do anything without electrical power.";
    $("power-explanation").textContent = explanation;
    const prefix = p.regulated && p.usb ? ["Two parallel inputs: battery via regulator + D1, or USB via VBUS + on-board diode (may share)"] : p.regulated ? ["AA pack", "Fuse + master", "External regulator: 5 V", "External diode D1"] : p.usb ? ["USB: 5 V", "VBUS · pad 40", "On-board diode"] : ["No active supply"];
    const chain = p.pico ? [...prefix, "VSYS · pad 39", "On-board regulator", "Chip: 3.3 V"] : [...prefix, "Pico off"];
    $("power-trace").innerHTML = chain.map(s => `<span class="trace-node">${esc(s)}</span>`).join('<span class="trace-arrow" aria-hidden="true">→</span>');
    document.querySelectorAll("[data-supply]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.supply === supply)));
  }
  document.querySelectorAll("[data-supply]").forEach(b => b.addEventListener("click", () => { supply = b.dataset.supply; updatePower(); }));
  $("master-on").addEventListener("change", updatePower);
  $("servo-request").addEventListener("change", updatePower);
  updatePower();

  function updateProgress() {
    const count = course.lessons.filter(completed).length;
    $("course-progress").max = course.lessons.length;
    $("course-progress").value = count;
    $("progress-label").textContent = `${count} / ${course.lessons.length} completed`;
    $("lesson-count").textContent = `${count}/${course.lessons.length}`;
    $("lesson-nav").innerHTML = course.lessons.map((lesson, i) => `<button type="button" data-lesson="${esc(lesson.id)}" ${lesson.id === currentLesson ? 'aria-current="step"' : ""}><span class="lesson-num">${completed(lesson) ? "✓" : String(i + 1).padStart(2, "0")}</span><span>${esc(lesson.title.replace(/^\d+\.\s*/, ""))}</span></button>`).join("");
    $("lesson-nav").querySelectorAll("button").forEach(b => b.addEventListener("click", () => { location.hash = "lesson/" + b.dataset.lesson; }));
  }
  function renderLesson(id) {
    const index = Math.max(0, course.lessons.findIndex(l => l.id === id));
    const lesson = course.lessons[index]; currentLesson = lesson.id;
    $("lesson-content").innerHTML = `<p class="eyebrow">LESSON ${index + 1} OF ${course.lessons.length}</p><h3 class="lesson-title">${esc(lesson.title.replace(/^\d+\.\s*/, ""))}</h3><p class="objective">${esc(lesson.objective)}</p>${paragraphs(lesson.concept)}<h4>In this project</h4>${paragraphs(lesson.project)}<div class="worked-example"><h3>Work through it</h3><p>${esc(lesson.example.prompt)}</p><ol>${lesson.example.steps.map(s => `<li>${esc(s)}</li>`).join("")}</ol><p><strong>${esc(lesson.example.answer)}</strong></p></div><div class="misconception"><p class="claim">Common misconception: ${esc(lesson.misconception.claim)}</p><p>${esc(lesson.misconception.correction)}</p></div><h3>Check your understanding</h3>${lesson.quiz.map((q, qi) => `<form class="quiz-block" data-quiz="${esc(q.id)}"><fieldset><legend>${qi + 1}. ${esc(q.question)}</legend>${q.options.map((option, i) => `<label class="quiz-option"><input type="radio" name="answer" value="${i}" ${answers[q.id] === i ? "checked" : ""} required><span>${esc(option)}</span></label>`).join("")}</fieldset><button type="submit">Check answer</button><div class="quiz-feedback" aria-live="polite">${feedback(q)}</div></form>`).join("")}<div class="lesson-sources">Fact-check sources: ${sourceLinks(lesson.source_ids)}</div><div class="lesson-actions">${index ? `<button type="button" id="previous-lesson">← Previous lesson</button>` : '<span></span>'}${index < course.lessons.length - 1 ? `<button type="button" id="next-lesson">Next lesson →</button>` : '<a class="button" href="#workbench/design">Try the design challenge →</a>'}</div>`;
    $("lesson-content").querySelectorAll("form").forEach(form => form.addEventListener("submit", e => {
      e.preventDefault(); const q = lesson.quiz.find(q => q.id === form.dataset.quiz);
      const value = Number(new FormData(form).get("answer"));
      if (!Number.isInteger(value) || value < 0 || value >= q.options.length) return;
      answers[q.id] = value; save(); form.querySelector(".quiz-feedback").innerHTML = feedback(q); updateProgress();
    }));
    if ($("previous-lesson")) $("previous-lesson").onclick = () => { location.hash = "lesson/" + course.lessons[index - 1].id; };
    if ($("next-lesson")) $("next-lesson").onclick = () => { location.hash = "lesson/" + course.lessons[index + 1].id; };
    updateProgress();
  }
  function feedback(q) {
    if (!Object.prototype.hasOwnProperty.call(answers, q.id)) return "";
    const correct = answers[q.id] === q.answer_index;
    return `<p class="feedback ${correct ? "" : "error"}"><strong>${correct ? "Correct." : "Try again."}</strong> ${esc(q.explanation)}</p>`;
  }
  $("course-sources").innerHTML = `<h3>Scope</h3><ul>${course.scope.map(s => `<li>${esc(s)}</li>`).join("")}</ul><h3>Still uncertain</h3><ul>${course.uncertainties.map(s => `<li>${esc(s)}</li>`).join("")}</ul><h3>Primary references</h3>${course.sources.map(s => `<div><a href="${safeUrl(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a><ul>${s.claims.map(c => `<li>${esc(c)}</li>`).join("")}</ul></div>`).join("")}`;
  $("reset-progress").onclick = () => { answers = {}; save(); renderLesson(currentLesson); };
  $("checked-date").textContent = "Sources checked " + course.checked_date;

  const slider = (id, label, min, max, step, value, unit) => `<label for="${id}"><span>${label}<output id="${id}-value" for="${id}">${value} ${unit}</output></span><input id="${id}" type="range" min="${min}" max="${max}" step="${step}" value="${value}" data-unit="${unit}"></label>`;
  function bindSliders(update) {
    $("lab-content").querySelectorAll("input").forEach(input => input.addEventListener("input", () => {
      const out = $(input.id + "-value"); if (out) out.textContent = input.value + " " + input.dataset.unit;
      update();
    })); update();
  }
  const n = id => Number($(id).value);
  const voltageSvg = `<svg class="lab-svg" viewBox="0 0 440 180" role="img" aria-label="A source, resistor and return form a complete loop"><path d="M80 60H175l7-12 12 24 12-24 12 24 12-24 12 24 7-12H360V140H80V100M60 100H100M68 87H92M80 87V60" fill="none" stroke="currentColor" stroke-width="2"/><text x="100" y="93">source</text><text x="165" y="28">known resistor</text><text x="162" y="166">complete return path</text></svg>`;
  function renderLab(name) {
    if (!["ohm","divider","pwm","capacitor","energy","design"].includes(name)) name = "ohm";
    currentLab = name;
    document.querySelectorAll("[data-lab]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.lab === name)));
    if (name === "ohm") {
      $("lab-content").innerHTML = `<h3>Current is the result, not a number the supply forces.</h3><p>Predict what happens when you double the resistance at the same voltage.</p><div class="lab-layout"><div class="lab-controls">${slider("ohm-v","Supply voltage",1,6,0.1,5,"V")}${slider("ohm-r","Resistance",100,2000,100,1000,"Ω")}</div><div class="lab-result">${voltageSvg}<div class="result-big" id="ohm-current"></div><div class="result-caption" id="ohm-power"></div><div class="formula" id="ohm-formula"></div></div></div><p class="lab-notes">This is a known resistor, not a model of a servo. Motors and their control electronics draw changing current with position, load and startup. A supply's “2 A” rating describes a capability under specified conditions; it does not force 2 A into every load. In our circuit, the 1 kΩ bleeder draws 5 mA and dissipates 0.025 W at 5 V.</p>`;
      bindSliders(() => { const r = M.ohm(n("ohm-v"), n("ohm-r")); $("ohm-current").textContent = `${(r.amps*1000).toFixed(2)} mA`;
        $("ohm-power").textContent = `${r.watts.toFixed(3)} W dissipated in the resistor${r.watts > 0.25 ? " — above a ¼ W rating; choose an adequately rated resistor." : " — below a ¼ W rating; allow operating margin."}`; $("ohm-formula").textContent = `I = V ÷ R = ${n("ohm-v")} ÷ ${n("ohm-r")} = ${r.amps.toFixed(4)} A`; });
    } else if (name === "divider") {
      $("lab-content").innerHTML = `<h3>Make the battery voltage measurable.</h3><p>Try the selected 100 kΩ / 47 kΩ pair, then see what happens if the lower resistor grows.</p><div class="lab-layout"><div class="lab-controls">${slider("div-v","Raw pack voltage",0,6.4,0.1,4.8,"V")}${slider("div-top","Top resistor",10,200,1,100,"kΩ")}${slider("div-bottom","Bottom resistor",10,200,1,47,"kΩ")}</div><div class="lab-result"><svg class="lab-svg" viewBox="0 0 440 190" role="img" aria-label="Pack positive to top resistor, ADC midpoint, bottom resistor and ground"><path d="M100 10V30l-10 6 20 8-20 8 20 8-10 6V95m0 0H270m-170 0v15l-10 6 20 8-20 8 20 8-10 6V165m-20 0h40m-32 8h24m-18 7h12" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="100" cy="95" r="4" fill="currentColor"/><text x="126" y="49">R top</text><text x="126" y="135">R bottom</text><text x="277" y="101">GP26</text><text x="13" y="20">pack +</text></svg><div class="result-big" id="div-result"></div><div id="div-meter" class="meter"><span></span></div><p id="div-warning" aria-live="polite"></p><div class="formula" id="div-formula"></div><p class="result-caption" id="div-detail"></p></div></div><p class="lab-notes">The real circuit adds a 100 nF filter capacitor and 1% resistors. These calculations assume an unloaded divider and ideal 3.3 V ADC reference; they omit tolerance, noise and sampling error. The displayed 12-bit code is ideal; MicroPython read_u16() scales its reading to 0–65535. Verify the measured node and scale before enabling sensing. Sensing raw pack voltage is different from measuring regulated VSYS.</p>`;
      bindSliders(() => { const r = M.divider(n("div-v"),n("div-top"),n("div-bottom")); $("div-result").textContent = `${r.volts.toFixed(3)} V at GP26`;
        $("div-meter").classList.toggle("over", !r.safeNominal); $("div-meter").firstElementChild.style.width = `${Math.min(100,r.volts/3.3*100)}%`;
        $("div-warning").textContent = r.safeNominal ? "Within the nominal 0–3.3 V range. Leave margin for tolerances." : "Above 3.3 V: revise the divider. An ADC is not a safe voltage clamp.";
        $("div-formula").textContent = `Vnode = ${n("div-v")} × ${n("div-bottom")} ÷ (${n("div-top")} + ${n("div-bottom")})`;
        $("div-detail").textContent = `${r.microamps.toFixed(1)} µA continuous divider current · scale ×${r.scale.toFixed(3)} · ${r.safeNominal ? 'ideal 12-bit code '+r.ideal12bit : 'out of range; do not wire this combination'}`; });
    } else if (name === "pwm") {
      $("lab-content").innerHTML = `<h3>Pulse timing tells the servo where to go.</h3><p>Change pulse width while the repeat interval stays 20 ms (50 Hz).</p><div class="lab-layout"><div class="lab-controls">${slider("pwm-width","High pulse width",1,2,0.05,1.5,"ms")}<p class="subtle">This is a teaching range, not an approved travel range for your MG90S or installed mechanism.</p></div><div class="lab-result"><svg id="pwm-svg" class="lab-svg" viewBox="0 0 520 200" role="img" aria-label="3.3-volt servo control signal over one 20-millisecond period"><path d="M40 20V150H490" fill="none" stroke="currentColor" stroke-width="1"/><text x="0" y="60">3.3 V</text><text x="9" y="144">0 V</text><path id="pulse-path" fill="none" stroke="var(--blue)" stroke-width="3"/><text x="37" y="177">0</text><text x="446" y="177">20 ms</text></svg><div class="result-big" id="pwm-result"></div><p id="pwm-caption"></p></div></div><p class="lab-notes">The signal wire carries timing; the separate 5 V wire carries motor power. A pulse near 1.5 ms commonly requests a middle position, but angle, direction, endpoints and accepted 3.3 V signal levels depend on the actual servo. Our installed yoke needs a very small calibrated movement, not a 180° sweep. Stopping PWM does not physically disconnect the servo supply.</p>`;
      bindSliders(() => { const width=n("pwm-width"), end=40+width/20*440; $("pulse-path").setAttribute("d",`M40 140V50H${end}V140H480`); $("pwm-result").textContent=`${width.toFixed(2)} ms HIGH`; $("pwm-caption").textContent=`${(20-width).toFixed(2)} ms LOW · ${(width/20*100).toFixed(2)}% duty cycle. Pulse width is the position command; no universal angle is implied.`; });
    } else if (name === "capacitor") {
      $("lab-content").innerHTML = `<h3>A capacitor buys a little time.</h3><p>Start with an ideal capacitor charged to 5 V. Disconnect its source and draw constant current. Predict how far its voltage falls.</p><div class="lab-layout"><div class="lab-controls">${slider("cap-c","Capacitance",100,2200,10,470,"µF")}${slider("cap-i","Load current",0,1000,10,500,"mA")}${slider("cap-t","Time without supply",0,10,0.1,1,"ms")}</div><div class="lab-result"><div class="result-caption">Ideal capacitor voltage after the interruption</div><div class="result-big" id="cap-result"></div><div class="meter"><span id="cap-level"></span></div><p id="cap-detail" aria-live="polite"></p><div class="formula" id="cap-formula"></div></div></div><p class="lab-notes">ΔV = I × Δt ÷ C until the ideal capacitor is depleted. This model has no connected regulator, wiring inductance, equivalent series resistance, leakage or changing motor current. It is not a prediction of servo-rail voltage. A larger capacitance reduces brief droop, but adds stored energy and charging demand. The selected C1 is rated 10 V on a 5 V rail; its polarity still matters.</p>`;
      bindSliders(() => {const r=M.capacitor(n("cap-c"),n("cap-i"),n("cap-t"));$("cap-result").textContent=`${r.volts.toFixed(2)} V`;$("cap-level").style.width=`${r.volts/5*100}%`;$("cap-detail").textContent=r.depleted?"Depleted before or at this time. The assumed constant current cannot continue from this capacitor alone.":`${r.drop.toFixed(2)} V drop. Initially stored energy: ${(r.initialJoules*1000).toFixed(2)} mJ.`;$("cap-formula").textContent=`ΔV = (${n("cap-i")} ÷ 1000 A) × (${n("cap-t")} ÷ 1000 s) ÷ (${n("cap-c")} ÷ 1,000,000 F)`;});
    } else if (name === "energy") {
      $("lab-content").innerHTML = `<h3>Where does the battery's energy go?</h3><p>Compare radio-off waiting current with how often the servo moves. Adjust the waiting-current assumption below; other fixed assumptions are listed beneath the experiment.</p><div class="lab-layout"><div class="lab-controls">${slider("energy-cap","Cell capacity (series pack)",750,2500,50,1900,"mAh")}${slider("energy-sleep","Waiting logic at 5 V",1,50,1,10,"mA")}${slider("energy-interval","Poll interval",10,900,10,60,"s")}${slider("energy-actions","Total presses per day",0,200,10,20,"presses")}</div><div class="lab-result"><div class="result-caption">Illustrative energy estimate</div><div class="result-big" id="energy-result"></div><p id="energy-detail"></p><div class="energy-bars" aria-label="Daily battery energy by load"><span></span><span></span><span></span></div><div class="energy-legend"><span>Logic</span><span>Servo</span><span>Overhead</span></div><p id="energy-breakdown" class="subtle"></p></div></div><p class="lab-notes">Fixed assumptions: four 1.2 V NiMH cells; 80% accessible nominal energy; 85% conversion efficiency; 80 mA at 5 V for each 3-second connection/poll; 500 mA switched load for 1 second per complete press-and-return; 2.05 mA pack-side regulator/master-LED/divider overhead. Actuation time conservatively adds awake logic time. No deep sleep, peak-current capability, battery aging or radio reliability is proven. These match the repository's energy estimator. A 1 mA waiting value is an experimental scenario, not an achieved Pico current.</p>`;
      bindSliders(() => { const r=M.energy({capacityMah:n("energy-cap"),sleepMa:n("energy-sleep"),wakeMa:80,wakeSeconds:3,intervalSeconds:n("energy-interval"),actions:n("energy-actions"),servoMa:500,actionSeconds:1}); $("energy-result").textContent=`${r.days.toFixed(2)} days`;
        $("energy-detail").textContent=`${r.nominalWh.toFixed(2)} Wh nominal pack energy; ${r.accessibleWh.toFixed(2)} Wh accessible in this model.`;
        const terms=[r.logicWhDay,r.servoWhDay,r.parasiticWhDay]; $("lab-content").querySelectorAll(".energy-bars span").forEach((span,i)=>{span.style.width=`${terms[i]/r.totalWhDay*100}%`;});
        $("energy-breakdown").textContent=`Battery energy per day: logic ${r.logicWhDay.toFixed(3)} Wh · servo ${r.servoWhDay.toFixed(3)} Wh · overhead ${r.parasiticWhDay.toFixed(3)} Wh.`; });
    } else renderDesign();
    const labSources = {ohm:["ohm","power"],divider:["divider","adc","pico2"],pwm:["servo","pwm"],energy:["cells","regulator","firmware-local"],capacitor:["capacitors","gate"],design:["pico-power","gate","divider","meter-i"]};
    $("lab-content").insertAdjacentHTML("beforeend", `<p class="lesson-sources">Fact-check sources: ${sourceLinks(labSources[name])}</p>`);
  }
  const designQuestions = [
    ["Where does the external regulated 5 V branch enter the Pico?",["Directly into GP15","Through our diode D1 into VSYS, pad 39","Into 3V3 OUT, pad 36"],1,"VSYS feeds the on-board 3.3 V regulator. The external diode prevents USB-derived power flowing back into the motor rail."],
    ["Where does the servo get its motor current?",["From the 5 V regulator through the servo gate","From GP16","From the battery ADC node"],0,"The GPIO sends timing or enable logic. The regulator and MOSFET power path carry the motor current."],
    ["Which way does our supply diode D1 face?",["Stripe toward the regulator","Either way","Stripe toward Pico VSYS"],2,"The cathode stripe faces VSYS. Normal external supply current can flow from anode at 5 V toward the cathode."],
    ["What connects to the servo's ground wire?",["Nothing; PWM provides the return","The common GND, returned directly to the power assembly","The Pico's 3V3 output"],1,"A complete power loop and a shared signal reference are both needed. Keep motor current out of the Pico wiring."],
    ["How should GP26 sense a changing battery?",["Connect the raw pack directly","Use the regulated 5 V rail","Use the 100 kΩ / 47 kΩ divider from master-switched raw pack, with 100 nF to GND"],2,"The divider reduces the raw voltage. Measuring the regulated rail would conceal much of the battery discharge."],
    ["How is the servo gate kept off during Pico reset?",["A 100 kΩ ON-to-GND pulldown and the gate's physical slider OFF","A 100 kΩ resistor to 5 V","Only by the first line of main.py"],0,"Hardware establishes the default before firmware starts. Leaving the gate's slide switch ON defeats GPIO shutdown."],
    ["Before attaching the Pico, what measurement comes first?",["Place a current-mode meter across battery + and −","Check polarity, continuity with power removed, then regulator voltage in voltage mode","Drive both servos against the wall switch"],1,"Resistance/continuity are unpowered checks. Voltage is measured across nodes. Current mode across a supply can create a short."],
    ["What must happen before a full enclosure print and wall installation?",["Only check that the STL opens","Assume every MG90S is identical","Test component coupons and actual dimensions; verify small travel and a suitable mounting method"],2,"Nominal CAD and manifold checks cannot prove actual tolerances, horn geometry, cable routing or adhesion. The selected Command strips exclude textured walls."]
  ];
  function renderDesign() {
    $("lab-content").innerHTML = `<h3>Design the circuit before seeing the answer.</h3><p>Choose each connection or check below. Then compare your reasoning with the source-backed lesson and full connection sheet.</p><form id="design-form">${designQuestions.map((q,i)=>`<div class="design-row"><label for="design-${i}">${i+1}. ${esc(q[0])}</label><select id="design-${i}" required><option value="">Choose an answer</option>${q[1].map((o,j)=>`<option value="${j}">${esc(o)}</option>`).join("")}</select><div id="design-feedback-${i}" aria-live="polite"></div></div>`).join("")}<div class="design-controls"><button type="submit">Check my design</button><span id="design-score" aria-live="polite"></span></div></form><details><summary>Continue to the full design brief</summary><h3>${esc(course.capstone.title)}</h3><p>${esc(course.capstone.brief)}</p>${course.capstone.steps.map(s=>`<h4>${esc(s.title)}</h4><p>${esc(s.prompt)}</p><details><summary>Show expected reasoning</summary><p>${esc(s.expected)}</p><p>${sourceLinks(s.source_ids)}</p></details>`).join("")}<h4>Bench checklist</h4><ul>${course.capstone.checklist.map(s=>`<li>${esc(s)}</li>`).join("")}</ul></details>`;
    $("design-form").onsubmit = e => {e.preventDefault(); let score=0;designQuestions.forEach((q,i)=>{const raw=$("design-"+i).value;const correct=raw!==""&&Number(raw)===q[2];if(correct)score++;$("design-feedback-"+i).innerHTML=`<p class="feedback ${correct?"":"error"}"><strong>${correct?"Correct.":"Revisit this choice."}</strong> ${esc(q[3])}</p>`;});$("design-score").textContent=`${score} / ${designQuestions.length} correct. ${score===designQuestions.length?"Now explain each branch aloud and compare with the diagram.":"Revise the marked choices and try again."}`;};
  }
  document.querySelectorAll("[data-lab]").forEach(b=>b.addEventListener("click",()=>{location.hash="workbench/"+b.dataset.lab;}));

  function renderBom() {
    const gang=$("gang-count").value;const query=$("bom-search").value.toLowerCase();
    $("print-body").innerHTML=Object.entries(data.fit.installed_print_counts[gang]).sort(([a],[b])=>a.localeCompare(b)).map(([file,count])=>`<tr><td><a href="https://github.com/eoinest/auto-switch/blob/main/hardware/cad/generated/${encodeURIComponent(file)}" target="_blank" rel="noopener">${esc(file)}</a></td><td>${count}</td></tr>`).join("");
    const rows=data.bom.filter(row=>Number(row["quantity_"+(gang==="1"?"one":"two")+"_gang"])>0&&Object.values(row).join(" ").toLowerCase().includes(query));
    $("bom-count").textContent=`${rows.length} matching BOM entries for ${gang==="1"?"one switch":"two switches"}. Quantity units distinguish installed pieces from shared consumables.`;
    $("bom-body").innerHTML=rows.map(row=>`<tr><td><strong>${esc(row.part)}</strong><small>${esc(row.category)} · ${esc(row.id)}</small></td><td>${esc(row["quantity_"+(gang==="1"?"one":"two")+"_gang"])}<small>${esc(row.unit)}</small></td><td><strong>${esc(row.fit_status)}</strong><small class="filename">${esc(row.stl_files)}</small><small>${esc(row.notes)}</small></td><td>${row.purchase_url?`<a href="${safeUrl(row.purchase_url)}" target="_blank" rel="noopener">Buy / select ↗</a><br>`:""}${row.source_url?`<a href="${safeUrl(row.source_url)}" target="_blank" rel="noopener">Specification ↗</a>`:""}</td></tr>`).join("");
  }
  $("gang-count").onchange=renderBom;$("bom-search").oninput=renderBom;
  $("fit-summary").innerHTML=`<div class="fit-summary"><h3>Digital fit evidence ≠ a physically tested assembly.</h3><p>The fit report and BOM map selected components to current STL files. Checks cover the specific dimensions and geometry named in that report; actual servo/horn, solder, connector and wallplate measurements remain necessary. Start with the small fit coupons. The selected Command strips are unsuitable for the pictured textured wall.</p><p><a href="assets/bom-fit-report.json" target="_blank" rel="noopener">Inspect fit evidence ↗</a> · <a href="assets/BOM.md" target="_blank" rel="noopener">Complete written BOM ↗</a></p></div>`;
  $("fit-report").textContent=JSON.stringify(data.fit,null,2);renderBom();

  function route() {
    const [section,id]=location.hash.slice(1).split("/");
    const page=section==="lesson"?"lessons":["wiring","breadboard","power","lessons","workbench","parts"].includes(section)?section:"wiring";
    document.querySelectorAll(".page").forEach(p=>{p.hidden=p.id!=="page-"+page;});
    document.querySelectorAll("[data-page]").forEach(a=>{if(a.dataset.page===page)a.setAttribute("aria-current","page");else a.removeAttribute("aria-current");});
    if(page==="breadboard")requestAnimationFrame(()=>zoomBreadboard(bbZoom));
    if(page==="wiring")requestAnimationFrame(() => zoomMap(mapZoom));
    if(page==="lessons")renderLesson(id||currentLesson);
    if(page==="workbench")renderLab(id||currentLab);
  }
  updateProgress();window.addEventListener("hashchange",route);route();
})();
