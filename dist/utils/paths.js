import path from "node:path";
export function toAbsolutePath(baseDir, targetPath) {
    return path.isAbsolute(targetPath)
        ? path.normalize(targetPath)
        : path.resolve(baseDir, targetPath);
}
export function toPosixRelativePath(baseDir, targetPath) {
    return path.relative(baseDir, targetPath).split(path.sep).join(path.posix.sep);
}
//# sourceMappingURL=paths.js.map