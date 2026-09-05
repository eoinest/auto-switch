# Learn the Auto Switch circuit

Open `index.html` directly in a browser, or serve this folder locally from the repository root:

```sh
python3 -m http.server 8766 --bind 127.0.0.1 --directory learn
```

Then visit **http://127.0.0.1:8766**. There is no package installation, account, CDN, analytics, or connection to a real Pico. The learning module never sends device commands. External reference and purchase links need internet access, but the bundled lessons, experiments, diagrams and BOM work offline. Progress is stored in this browser when local storage is available; file-URL storage behavior varies by browser.

## Suggested path

1. Start with **Connection map** to see the entire circuit. Use **Fit entire map**, zoom, or **Full screen**. Then in **Power explorer**, compare Battery, USB and Both. Turn the battery master off while USB remains plugged in. Predict why the Pico is awake but the servo rail stays off.
2. Follow the **12 guided lessons** in order. Work the example before looking at its answer, then answer both questions. Explanations remain available after a wrong answer, and you can retry.
3. Use the **Workbench** to vary resistance, design a battery voltage divider, inspect pulse timing, explore capacitor droop and estimate energy. Each experiment names its assumptions and source references.
4. Complete **Design it yourself**. Its eight checks and six-step open design brief ask you to choose the connections and explain why they work.
5. In **Parts & fit**, choose one or two switches. Search the complete BOM, inspect each STL mapping, and read the fit evidence before buying or printing.

The **Breadboard** tab adds a matching bench layout for the existing headered Pico: choose one or two servos, highlight a build step, and follow the component/jumper table. The downloadable guide includes bench-only purchases and first-power checks.

## Sources and limits

The curriculum and claim-level source registry are in [`docs/learn-content.json`](../docs/learn-content.json) and [`docs/learn-sources.md`](../docs/learn-sources.md). Core references are manufacturer documentation from Raspberry Pi, Pololu, Panasonic, SCHURTER, SparkFun and Adafruit, plus MicroPython documentation. Project-specific firmware behavior is labeled as a project claim, not independent manufacturer evidence.

The power map illustrates nominal steady states and source availability. It does not calculate transient behavior, exact diode drops or current sharing. The battery calculator uses explicit assumptions, not measured runtime. The fit report separates digital geometry checks from unverified physical parts and mounting. The selected board is a headerless Pico W; a different board or horn needs its own fit check.

## Rebuild and verify

The site bundles source material so `file://` use does not depend on network fetches. Edit the source curriculum, hardware diagrams or BOM, then rebuild:

```sh
python3 tools/render_wiring.py
python3 tools/build_learning.py
python3 tools/build_learning.py --check
node tests/test_learning_model.cjs
python3 -m unittest discover -s tests -v
```

`build_learning.py` includes source hashes and copies only the public educational assets into `learn/assets`. Serve this folder, not the repository root containing development configuration. The generated `data.js` should not be edited by hand.
