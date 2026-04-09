import fg from "fast-glob";
import fs from "fs-extra";
import path from "node:path";
import { parseContentFile } from "./parser.js";
export async function scanContent(contentRoot) {
    const pattern = path.posix.join(contentRoot.split(path.sep).join(path.posix.sep), "**/*.md");
    const files = await fg(pattern, {
        onlyFiles: true,
        dot: false
    });
    const items = await Promise.all(files.map(async (filePath) => {
        const absolutePath = path.resolve(filePath);
        const fileContent = await fs.readFile(absolutePath, "utf8");
        const relativePath = path.relative(contentRoot, absolutePath);
        return parseContentFile(fileContent, absolutePath, relativePath);
    }));
    return items.sort((left, right) => left.id.localeCompare(right.id));
}
//# sourceMappingURL=scanner.js.map