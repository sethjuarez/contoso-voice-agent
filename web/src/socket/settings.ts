export interface Settings {
  threshold: number;
  silence: number;
  prefix: number;
}

export const getSettings = (): Settings => {
  const settingsString = localStorage.getItem("voice-settings");
  if (settingsString) {
    return JSON.parse(settingsString);
  } else {
    localStorage.setItem(
      "voice-settings",
      JSON.stringify({ threshold: 0.8, silence: 500, prefix: 300 })
    );
    return {
      threshold: 0.8,
      silence: 500,
      prefix: 300,
    };
  }
};
