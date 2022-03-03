<template>
  <v-row justify="center" align="center">
    <v-col cols="12" sm="8" md="6">
      <div class="text-center pb-3">
        <SH365Logo />
      </div>
      <v-card>
        <v-card-title class="title"> 質問 </v-card-title>
        <v-card-text>
          お使いのキーボード、マイクの機種名と日本語入力ソフト
          (IME)を教えてください。

          <v-text-field
            v-model="keyboard_name"
            label="キーボードの機種名 (ノートパソコンの場合は機種名)"
            hide-details="auto"
            class="pb-4 pt-6"
          ></v-text-field>
          <v-text-field
            v-model="mic_name"
            label="マイクの機種名"
            hide-details="auto"
            class="pb-4"
          ></v-text-field>
          <v-select
            v-model="ime_name"
            :items="[
              'Microsoft 日本語 IME',
              'Google 日本語入力',
              'ATOK',
              'Apple 日本語IM',
              'かわせみ',
              'Mozc',
              'その他',
            ]"
            label="日本語入力ソフト (IME)"
            class=""
          ></v-select>
          <v-textarea v-model="additional_text" label="追加情報"></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-btn active-class="no-active" color="primary" nuxt to="/">
            戻る
          </v-btn>
          <v-spacer />
          <v-btn active-class="no-active" color="primary" @click="nextPage">
            次へ
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'Question',
  data() {
    return {
      keyboard_name: '',
      mic_name: '',
      ime_name: '',
      additional_text: '',
    }
  },
  computed: {
    wizard_step() {
      return this.$store.state.wizard.step
    },
    questions() {
      return this.$store.state.question.questions
    },
  },
  mounted() {
    this.checkWizardStep()
    this.updateWizardStep()
    this.loadDataFromStore()
  },
  methods: {
    checkWizardStep() {
      if (this.wizard_step < 1) {
        this.$router.push({ name: 'index' })
      }
    },
    updateWizardStep() {
      this.$store.commit('wizard/save', Math.max(this.wizard_step, 2))
    },
    loadDataFromStore() {
      this.keyboard_name = this.questions.keyboard
      this.mic_name = this.questions.mic
      this.ime_name = this.questions.ime
      this.additional_text = this.questions.additional_text
    },
    nextPage() {
      this.$store.commit('question/save', {
        keyboard: this.keyboard_name,
        mic: this.mic_name,
        ime: this.ime_name,
        additional_text: this.additional_text,
      })
      this.$router.push({ name: 'prepare' })
    },
  },
}
</script>

<style scoped></style>
