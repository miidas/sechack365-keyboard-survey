export const state = () => ({
  input_mode: '',
})

export const mutations = {
  save(state, text) {
    state.input_mode = text
  },
}
