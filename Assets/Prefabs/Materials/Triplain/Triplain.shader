Shader "Custom/URP/TriplanarGrid"
{
    Properties
    {
        [Toggle] _UseTexture ("Use Texture", Float) = 0
        _BaseMap ("Base Texture", 2D) = "white" {}
        _TextureScale ("Texture Scale", Float) = 1
        _GroundTint ("Ground Tint", Color) = (0.12, 0.16, 0.19, 1)
        _GridColor ("Grid Color", Color) = (0.2, 0.8, 1, 1)
        _GridSize ("Grid Size", Float) = 2
        _GridLineWidth ("Grid Line Width", Range(0.005, 0.2)) = 0.035
        _GridOpacity ("Grid Opacity", Range(0, 1)) = 0.8
        _BlendSharpness ("Triplanar Sharpness", Range(1, 16)) = 4
    }

    SubShader
    {
        Tags
        {
            "RenderPipeline" = "UniversalPipeline"
            "RenderType" = "Opaque"
            "Queue" = "Geometry"
        }

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            TEXTURE2D(_BaseMap);
            SAMPLER(sampler_BaseMap);

            CBUFFER_START(UnityPerMaterial)
                float4 _GroundTint;
                float4 _GridColor;
                float _UseTexture;
                float _TextureScale;
                float _GridSize;
                float _GridLineWidth;
                float _GridOpacity;
                float _BlendSharpness;
            CBUFFER_END

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                float4 shadowCoord : TEXCOORD2;
                half fogFactor : TEXCOORD3;
            };

            Varyings Vert(Attributes input)
            {
                Varyings output;

                VertexPositionInputs positions =
                    GetVertexPositionInputs(input.positionOS.xyz);

                VertexNormalInputs normals =
                    GetVertexNormalInputs(input.normalOS);

                output.positionCS = positions.positionCS;
                output.positionWS = positions.positionWS;
                output.normalWS = normals.normalWS;
                output.shadowCoord = GetShadowCoord(positions);
                output.fogFactor = ComputeFogFactor(positions.positionCS.z);

                return output;
            }

            float GridMask(float2 coord)
            {
                float2 repeated = frac(coord);
                float2 distanceToLine = min(repeated, 1.0 - repeated);
                float2 aa = max(fwidth(coord) * 1.25, 0.0001);

                float2 outside = smoothstep(
                    _GridLineWidth,
                    _GridLineWidth + aa,
                    distanceToLine
                );

                return 1.0 - min(outside.x, outside.y);
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float3 positionWS = input.positionWS;
                half3 normalWS = normalize(input.normalWS);

                half3 weights = pow(
                    abs(normalWS),
                    max(_BlendSharpness, 1.0)
                );

                weights /= max(weights.x + weights.y + weights.z, 0.001);

                half3 color;

                if (_UseTexture > 0.5)
                {
                    float scale = max(_TextureScale, 0.001);

                    half3 texX = SAMPLE_TEXTURE2D(
                        _BaseMap, sampler_BaseMap, positionWS.zy * scale
                    ).rgb;

                    half3 texY = SAMPLE_TEXTURE2D(
                        _BaseMap, sampler_BaseMap, positionWS.xz * scale
                    ).rgb;

                    half3 texZ = SAMPLE_TEXTURE2D(
                        _BaseMap, sampler_BaseMap, positionWS.xy * scale
                    ).rgb;

                    color = (
                        texX * weights.x +
                        texY * weights.y +
                        texZ * weights.z
                    ) * _GroundTint.rgb;
                }
                else
                {
                    float size = max(_GridSize, 0.001);

                    float gridX = GridMask(positionWS.zy / size);
                    float gridY = GridMask(positionWS.xz / size);
                    float gridZ = GridMask(positionWS.xy / size);

                    half grid = dot(
                        half3(gridX, gridY, gridZ),
                        weights
                    );

                    color = lerp(
                        _GroundTint.rgb,
                        _GridColor.rgb,
                        grid * saturate(_GridOpacity)
                    );
                }

                Light mainLight = GetMainLight(input.shadowCoord);

                half diffuse = saturate(dot(normalWS, mainLight.direction));
                half3 ambient = SampleSH(normalWS);

                half3 lighting = ambient +
                    mainLight.color *
                    diffuse *
                    mainLight.distanceAttenuation *
                    mainLight.shadowAttenuation;

                color *= lighting;
                color = MixFog(color, input.fogFactor);

                return half4(color, 1);
            }
            ENDHLSL
        }

        UsePass "Universal Render Pipeline/Lit/ShadowCaster"
        UsePass "Universal Render Pipeline/Lit/DepthOnly"
        UsePass "Universal Render Pipeline/Lit/DepthNormals"
    }

    FallBack Off
}