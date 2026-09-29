/**
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";

Config.setRspack(true);
// Lossless frames keep every pixel edge crisp before encoding.
Config.setVideoImageFormat("png");
Config.setOverwriteOutput(true);
