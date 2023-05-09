// filename: inlang.config.js

export async function defineConfig(env) {
  // importing a plugin
  const plugin = await env.$import(
    "https://cdn.jsdelivr.net/gh/jannesblobel/inlang-plugin-po@1/dist/index.js"
  );

  // most plugins require additional config, read the plugins documentation
  // for the required config and correct usage.
  const pluginConfig = {
    pathPattern:
      "./rest_framework_simplejwt/locale/{language}/LC_MESSAGES/django.po",
    referenceResourcePath: null,
  };

  return {
    referenceLanguage: "en",
    languages: [
      "en",
      "cs",
      "de",
      "es",
      "es_AR",
      "es_CL",
      "fa_IR",
      "fr",
      "id_ID",
      "it_IT",
      "ko_KR",
      "nl_NL",
      "pl_PL",
      "pt_BR",
      "ro",
      "ru_RU",
      "sl",
      "sv",
      "tr",
      "uk_UA",
      "zh_Hans",
    ],
    readResources: (args) =>
      plugin.readResources({ ...args, ...env, pluginConfig }),
    writeResources: (args) =>
      plugin.writeResources({ ...args, ...env, pluginConfig }),
  };
}
