<template>
  <v-row justify="center" align="center">
    <v-col cols="12" sm="8" md="6">
      <div class="text-center pb-3">
        <SH365Logo />
      </div>
      <v-card>
        <v-card-title class="title"> キーボード入力に係わる調査 </v-card-title>
        <v-card-text>
          <p>
            このウェブサイトでは、Keyboard Acoustic
            Emanationの攻撃可能性、タイピングスタイル及び変換スタイルの調査を目的にキーボードの入力操作とマイク音声をリアルタイムに取得します。<br />
            調査に協力できる方のみ"次へ"をクリックしてください。<br />
            また、キーボードの打鍵音の録音のため、静かな環境で実施いただけると幸いです。<br />
            特に時間制限はありませんので、ゆっくりと入力していただければと思います。
          </p>
          <p>何か質問等ございましたら、TypeTalk@miidasまでご連絡ください。</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn active-class="no-active" color="primary" nuxt to="/question">
            次へ
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import SH365Logo from '~/components/SH365Logo.vue'

export default {
  name: 'Index',
  components: {
    SH365Logo,
  },
  computed: {
    wizard_step() {
      return this.$store.state.wizard.step
    },
  },
  mounted() {
    this.updateWizardStep()
  },
  methods: {
    updateWizardStep() {
      this.$store.commit('wizard/save', 1)
    },
  },
}
</script>
