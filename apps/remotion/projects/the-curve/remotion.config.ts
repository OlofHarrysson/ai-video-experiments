/**
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
Config.setVideoImageFormat("png");
Config.setOverwriteOutput(true);
// Three.js needs a real WebGL context in the headless browser.
Config.setChromiumOpenGlRenderer("angle");
