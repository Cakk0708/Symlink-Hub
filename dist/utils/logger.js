import pc from "picocolors";
export function info(message) {
    console.log(pc.cyan(message));
}
export function success(message) {
    console.log(pc.green(message));
}
export function warn(message) {
    console.warn(pc.yellow(message));
}
export function error(message) {
    console.error(pc.red(message));
}
//# sourceMappingURL=logger.js.map