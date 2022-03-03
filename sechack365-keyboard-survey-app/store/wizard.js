export const state = () => ({
  step: 0,
})

export const mutations = {
  save(state, step) {
    state.step = step
  },
}
