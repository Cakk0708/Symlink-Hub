import path from "node:path";

export function toAbsolutePath(baseDir: string, targetPath: string): string {
  return path.isAbsolute(targetPath)
    ? path.normalize(targetPath)
    : path.resolve(baseDir, targetPath);
}

export function toPosixRelativePath(baseDir: string, targetPath: string): string {
  return path.relative(baseDir, targetPath).split(path.sep).join(path.posix.sep);
}
