/**
 * Show and hide top level containers.
 *
 * @param name - The container to show. Hide the others.
 */
export function showHide(name) {
    const containers = ["grid", "canvas", "expand", "parts"]
    for (const c of containers) {
        document.getElementById(c + "-container").style.display = (name === c) ? "block" : "none"
    }
    document.getElementById("props").style.display = "none"
}
