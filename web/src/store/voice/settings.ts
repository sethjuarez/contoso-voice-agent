export interface Settings {
  threshold: number;
  silence: number;
  prefix: number;
  inputDeviceId: string;
  outputDeviceId: string;
}

export const getSettings = (): Settings => {
  const settingsString = localStorage.getItem("voice-settings");
  if (settingsString) {
    return JSON.parse(settingsString);
  } else {
    const defaultSettings: Settings = {
      threshold: 0.8,
      silence: 500,
      prefix: 300,
      inputDeviceId: "default",
      outputDeviceId: "default",
    };
    localStorage.setItem(
      "voice-settings",
      JSON.stringify(defaultSettings)
    );
    return defaultSettings;
  }
};