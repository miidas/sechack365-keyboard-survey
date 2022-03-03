export const state = () => ({
  questions: {},
})

export const mutations = {
  save(state, text) {
    state.questions = text
  },
}
