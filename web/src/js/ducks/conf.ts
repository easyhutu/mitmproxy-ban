/**
 * Conf houses properties about the current mitmproxy instance that are not options,
 * e.g. the list of available content views or the current version.
 */

interface ConfState {
    ip: string
    static: boolean
    version: string
    contentViews: string[]
}

// @ts-ignore
export const defaultState: ConfState = window.MITMWEB_CONF || {
    ip: "0.0.0.0",
    static: false,
    version: "1.2.3",
    contentViews: ["Auto", "Raw"],
};

export default function reducer(state = defaultState, action): ConfState {
    return state
}
