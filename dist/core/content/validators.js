export function validateUniqueContentIds(items) {
    const seen = new Map();
    for (const item of items) {
        const existing = seen.get(item.id);
        if (existing) {
            throw new Error(`Duplicate content id "${item.id}" found in "${existing}" and "${item.sourcePath}".`);
        }
        seen.set(item.id, item.sourcePath);
    }
}
//# sourceMappingURL=validators.js.map