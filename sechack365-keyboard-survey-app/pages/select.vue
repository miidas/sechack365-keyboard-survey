<template>
  <v-row justify="center" align="center">
    <v-col cols="12" sm="8" md="6">
      <div class="text-center pb-3">
        <SH365Logo />
      </div>
      <v-card>
        <v-card-title class="title"> 入力モードの選択 </v-card-title>
        <v-card-text>
          入力するテキストの種類を選択します
          <v-col cols="12" class="py-2 pt-5" align="center">
            <v-btn-toggle v-model="input_mode" color="blue darken-4">
              <v-btn value="word">
                <span class="hidden-sm-and-down">単語モード</span>
              </v-btn>

              <v-btn value="ss">
                <span class="hidden-sm-and-down">短文モード</span>
              </v-btn>

              <v-btn value="ls" disabled>
                <span class="hidden-sm-and-down">長文モード</span>
              </v-btn>
            </v-btn-toggle>
          </v-col>
        </v-card-text>
        <v-card-actions>
          <v-btn
            active-class="no-active"
            color="primary"
            @click="movePage('prepare')"
          >
            戻る
          </v-btn>
          <v-spacer />
          <v-btn
            active-class="no-active"
            color="primary"
            :disabled="!input_mode"
            @click="movePage('survey')"
          >
            次へ
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'Select',
  data() {
    return {
      input_mode: '',
    }
  },
  computed: {
    wizard_step() {
      return this.$store.state.wizard.step
    },
    select_mode() {
      return this.$store.state.select_mode.input_mode
    },
  },
  mounted() {
    this.checkWizardStep()
    this.updateWizardStep()
    this.loadDataFromStore()
  },
  methods: {
    checkWizardStep() {
      if (this.wizard_step < 3) {
        this.$router.push({ name: 'index' })
      }
    },
    updateWizardStep() {
      this.$store.commit('wizard/save', Math.max(this.wizard_step, 4))
    },
    loadDataFromStore() {
      this.input_mode = this.select_mode
    },
    movePage(pageName) {
      this.$store.commit('select_mode/save', this.input_mode)
      this.$router.push({ name: pageName })
    },
  },
}
</script>

<style scoped></style>
