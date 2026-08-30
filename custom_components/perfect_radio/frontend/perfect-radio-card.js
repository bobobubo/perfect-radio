class PerfectRadioCard extends HTMLElement {
  constructor() {
    super();

    this.attachShadow({ mode: "open" });

    this._hass = null;
    this._config = null;
    this._playing = false;
    this._pendingPlay = false;
    this._audio = new Audio();
  }

  static getStubConfig() {
    return {};
  }

  static getConfigForm() {
    return {
      schema: [],
    };
  }

  setConfig(config) {
    this._config = {
      entity: config.entity || null,
      title: config.title || "PERFECT RADIO",
    };

    this._render();
  }

  set hass(hass) {
    this._hass = hass;

    if (!this._config) {
      return;
    }

    this._update();

    if (this._pendingPlay) {
      const state = this._getState();

      if (state?.attributes?.stream_url) {
        this._pendingPlay = false;
        this._playCurrent();
      }
    }
  }

  getCardSize() {
    return 3;
  }

  _getState() {
    if (!this._hass) {
      return null;
    }

    if (this._config.entity) {
      return this._hass.states[this._config.entity] || null;
    }

    for (const [entityId, state] of Object.entries(this._hass.states)) {
      if (
        entityId.startsWith("select.") &&
        state.attributes.station_id !== undefined &&
        state.attributes.stream_url !== undefined
      ) {
        return state;
      }
    }

    return null;
  }

  _render() {
    this.shadowRoot.innerHTML = `
      <style>
        ha-card {
          padding: 18px;
        }

        .title {
          text-align: center;
          font-weight: 600;
          font-size: 18px;
          margin-bottom: 18px;
        }

        .station-row {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .label {
          white-space: nowrap;
        }

        select {
          flex: 1;
          min-width: 0;
          padding: 8px 10px;
          border-radius: 8px;
          font-size: 14px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          border: 1px solid var(--divider-color);
        }

        .buttons {
          display: flex;
          justify-content: center;
          gap: 24px;
          margin-top: 18px;
        }

        button {
          border: none;
          border-radius: 8px;
          padding: 9px 18px;
          cursor: pointer;
          font-size: 14px;
          background: var(--secondary-background-color);
          color: var(--primary-text-color);
        }

        #play {
          background: #2e7d32;
          color: white;
        }

        #stop {
          background: #8b1e1e;
          color: white;
        }

        #play:hover:not(:disabled) {
          background: #388e3c;
        }

        #stop:hover:not(:disabled) {
          background: #a52727;
        }

        button:disabled {
          opacity: 0.35;
          cursor: default;
        }

        button:hover {
          background: var(--divider-color);
        }

        button:disabled {
          opacity: 0.4;
          cursor: default;
        }

        .status {
          text-align: center;
          margin-top: 12px;
          font-size: 12px;
          color: var(--secondary-text-color);
        }
      </style>

      <ha-card>
        <div class="title"></div>

        <div class="station-row">
          <span class="label">Stanice:</span>
          <select></select>
        </div>

        <div class="buttons">
          <button id="play">▶ Play</button>
          <button id="stop">■ Stop</button>
        </div>

        <div class="status"></div>
      </ha-card>
    `;

    this.shadowRoot.querySelector(".title").textContent =
      this._config.title;

    this.shadowRoot
      .querySelector("select")
      .addEventListener("change", (event) => {
        this._selectStation(event.target.value);
      });

    this.shadowRoot
      .querySelector("#play")
      .addEventListener("click", () => {
        this._playCurrent();
      });

    this.shadowRoot
      .querySelector("#stop")
      .addEventListener("click", () => {
        this._stop();
      });
  }

  _update() {
    const state = this._getState();

    if (!state) {
      this.shadowRoot.querySelector(".status").textContent =
        "Perfect Radio není dostupné.";
      return;
    }

    const select = this.shadowRoot.querySelector("select");
    const options = state.attributes.options || [];

    if (
      select.options.length !== options.length ||
      Array.from(select.options).some(
        (option, index) => option.value !== options[index]
      )
    ) {
      select.innerHTML = "";

      for (const option of options) {
        const element = document.createElement("option");
        element.value = option;
        element.textContent = option;
        select.appendChild(element);
      }
    }

    select.value = state.state;

    const playButton = this.shadowRoot.querySelector("#play");
    const stopButton = this.shadowRoot.querySelector("#stop");

    playButton.disabled = this._playing;
    stopButton.disabled = !this._playing;

    this.shadowRoot.querySelector(".status").textContent =
      this._playing
        ? `Hraje: ${state.state}`
        : `Vybráno: ${state.state}`;
  }

  async _selectStation(option) {
    const state = this._getState();

    if (!state) {
      return;
    }

    if (this._playing) {
      this._pendingPlay = true;
    }

    await this._hass.callService(
      "select",
      "select_option",
      {
        entity_id: state.entity_id,
        option: option,
      }
    );
  }

  async _playCurrent() {
    const state = this._getState();
    const url = state?.attributes?.stream_url;

    if (!url) {
      return;
    }

    if (this._audio.src !== url) {
      this._audio.src = url;
    }

    try {
      await this._audio.play();
      this._playing = true;
      this._update();
    } catch (error) {
      console.error("Perfect Radio playback failed:", error);

      this.shadowRoot.querySelector(".status").textContent =
        "Přehrávání se nepodařilo spustit.";
    }
  }

  _stop() {
    this._audio.pause();
    this._audio.removeAttribute("src");
    this._audio.load();

    this._playing = false;
    this._pendingPlay = false;

    this._update();
  }
}

customElements.define("perfect-radio-card", PerfectRadioCard);

window.customCards = window.customCards || [];

window.customCards.push({
  type: "perfect-radio-card",
  name: "Perfect Radio",
  preview: true,
  description: "Internet radio player using the Perfect Radio integration.",
});
