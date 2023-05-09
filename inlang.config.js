export async function defineConfig(env) {
	const { default: pluginJson } = await env.$import(
		'https://cdn.jsdelivr.net/gh/jannesblobel/inlang-plugin-po@1/dist/index.js'
	);

	const { default: standardLintRules } = await env.$import(
		'https://cdn.jsdelivr.net/gh/inlang/standard-lint-rules@2/dist/index.js'
	);

	return {
		referenceLanguage: 'en',
		plugins: [pluginJson({ 
			pathPattern: './resources/{language}.json',
			variableReferencePattern: ["{", "}"]
		}), standardLintRules()]
	};
}
