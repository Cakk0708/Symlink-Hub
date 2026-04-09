import matter from "gray-matter";
import { contentFrontmatterSchema } from "../../domain/content-item.js";
import { sha256 } from "../../utils/hash.js";
export function parseContentFile(fileContent, sourcePath, relativePath) {
    const parsed = matter(fileContent);
    const frontmatter = contentFrontmatterSchema.parse(parsed.data);
    return {
        ...frontmatter,
        body: parsed.content.trim(),
        sourcePath,
        relativePath,
        checksum: sha256(fileContent)
    };
}
//# sourceMappingURL=parser.js.map