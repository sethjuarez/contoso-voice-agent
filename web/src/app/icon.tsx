import { ImageResponse } from "next/og";
import { TbTent } from "react-icons/tb";

export const size = {
  width: 32,
  height: 32,
};

const Icon = () => {
  return new ImageResponse(<TbTent size={32} />, { ...size });
};

export default Icon;
