// screens/PredictScreen.js
// ──────────────────────────────────────────────────────────────────────────────
// Main input screen where users adjust soil parameters via sliders and text
// inputs, then submit to the FastAPI /predict endpoint.

import React, { useState, useRef } from "react";
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import Slider from "@react-native-community/slider";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { COLORS, SPACING, RADIUS, SHADOW } from "../constants/theme";
import { API_BASE_URL } from "../constants/api";

// ── Slider configuration for each input feature ──────────────────────────────
// min, max, step, unit, and description displayed to the user.
const FIELDS = [
  {
    key: "N",
    label: "Nitrogen (N)",
    icon: "flask",
    min: 0, max: 140, step: 1, unit: "kg/ha",
    desc: "Amount of nitrogen in soil. High N promotes leafy growth.",
    default: 50,
  },
  {
    key: "P",
    label: "Phosphorus (P)",
    icon: "flask",
    min: 5, max: 145, step: 1, unit: "kg/ha",
    desc: "Phosphorus supports root development and fruiting.",
    default: 50,
  },
  {
    key: "K",
    label: "Potassium (K)",
    icon: "flask",
    min: 5, max: 205, step: 1, unit: "kg/ha",
    desc: "Potassium strengthens stems and improves disease resistance.",
    default: 50,
  },
  {
    key: "temperature",
    label: "Temperature",
    icon: "thermometer",
    min: 8, max: 44, step: 0.1, unit: "°C",
    desc: "Average ambient temperature of the growing area.",
    default: 25,
  },
  {
    key: "humidity",
    label: "Humidity",
    icon: "water",
    min: 14, max: 100, step: 1, unit: "%",
    desc: "Relative humidity of air. High humidity suits tropical crops.",
    default: 70,
  },
  {
    key: "ph",
    label: "Soil pH",
    icon: "beaker",
    min: 3.5, max: 9, step: 0.1, unit: "pH",
    desc: "Soil acidity/alkalinity. Most crops prefer 5.5–7.5.",
    default: 6.5,
  },
  {
    key: "rainfall",
    label: "Rainfall",
    icon: "rainy",
    min: 20, max: 300, step: 1, unit: "mm",
    desc: "Annual average rainfall in the region.",
    default: 100,
  },
];

export default function PredictScreen({ navigation }) {
  // ── State: slider values ──────────────────────────────────────────────────
  const [values, setValues] = useState(
    Object.fromEntries(FIELDS.map((f) => [f.key, f.default]))
  );

  // ── City name for live weather (optional) ─────────────────────────────────
  const [city, setCity] = useState("");

  // ── Loading state while API call is in progress ───────────────────────────
  const [loading, setLoading] = useState(false);

  // ── Handle slider change ──────────────────────────────────────────────────
  const handleSlider = (key, val) => {
    setValues((prev) => ({ ...prev, [key]: parseFloat(val.toFixed(2)) }));
  };

  // ── Call the FastAPI /predict endpoint ────────────────────────────────────
  const handlePredict = async () => {
    setLoading(true);
    Keyboard.dismiss();

    const payload = { ...values };
    if (city.trim()) payload.city = city.trim();

    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || `Server error ${response.status}`);
      }

      const result = await response.json();

      // Navigate to result screen and pass all data
      navigation.navigate("Result", { result, inputs: values });
    } catch (error) {
      console.error("[PredictScreen] API error:", error.message);
      Alert.alert(
        "Prediction Failed",
        `Could not reach the API.\n\n${error.message}\n\n` +
          "Make sure the Python server is running:\n  uvicorn api.main:app --reload --host 0.0.0.0 --port 8000",
        [{ text: "OK" }]
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <View style={styles.container}>
        <StatusBar style="light" backgroundColor={COLORS.primaryDark} />

        {/* ── Header ─────────────────────────────────────────────────────── */}
        <LinearGradient
          colors={[COLORS.primaryDark, COLORS.primary]}
          style={styles.header}
        >
          <Text style={styles.headerTitle}>Soil Parameters</Text>
          <Text style={styles.headerSub}>
            Adjust sliders to match your field data
          </Text>
        </LinearGradient>

        {/* ── Scrollable sliders ─────────────────────────────────────────── */}
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {FIELDS.map((field) => (
            <View key={field.key} style={styles.fieldCard}>
              {/* Label row */}
              <View style={styles.fieldHeader}>
                <View style={styles.fieldIconWrap}>
                  <Ionicons name={field.icon} size={16} color={COLORS.primaryLight} />
                </View>
                <Text style={styles.fieldLabel}>{field.label}</Text>
                {/* Current value badge */}
                <View style={styles.valueBadge}>
                  <Text style={styles.valueText}>
                    {values[field.key].toFixed(field.step < 1 ? 1 : 0)} {field.unit}
                  </Text>
                </View>
              </View>

              {/* Description */}
              <Text style={styles.fieldDesc}>{field.desc}</Text>

              {/* Slider */}
              <Slider
                style={styles.slider}
                minimumValue={field.min}
                maximumValue={field.max}
                step={field.step}
                value={values[field.key]}
                onValueChange={(v) => handleSlider(field.key, v)}
                minimumTrackTintColor={COLORS.primaryLight}
                maximumTrackTintColor={COLORS.border}
                thumbTintColor={COLORS.accent}
              />

              {/* Min / Max labels */}
              <View style={styles.rangeRow}>
                <Text style={styles.rangeText}>{field.min}</Text>
                <Text style={styles.rangeText}>{field.max}</Text>
              </View>
            </View>
          ))}

          {/* ── Optional city input ───────────────────────────────────────── */}
          <View style={styles.fieldCard}>
            <View style={styles.fieldHeader}>
              <View style={styles.fieldIconWrap}>
                <Ionicons name="cloud" size={16} color={COLORS.info} />
              </View>
              <Text style={[styles.fieldLabel, { color: COLORS.info }]}>
                Live Weather (Optional)
              </Text>
            </View>
            <Text style={styles.fieldDesc}>
              Enter your city name to auto-fill temperature, humidity &amp;
              rainfall from OpenWeatherMap. Leave blank to use sliders.
            </Text>
            <TextInput
              style={styles.cityInput}
              placeholder="e.g. Mumbai, Delhi, Pune …"
              placeholderTextColor={COLORS.textMuted}
              value={city}
              onChangeText={setCity}
              returnKeyType="done"
              onSubmitEditing={Keyboard.dismiss}
            />
          </View>

          {/* ── Predict button ────────────────────────────────────────────── */}
          <TouchableOpacity
            style={[styles.predictBtn, loading ? styles.predictBtnDisabled : null]}
            onPress={handlePredict}
            disabled={loading}
            activeOpacity={0.85}
          >
            <LinearGradient
              colors={[COLORS.primaryLight, COLORS.primary]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={styles.predictGradient}
            >
              {loading ? (
                <>
                  <ActivityIndicator color="#fff" size="small" style={{ marginRight: 8 }} />
                  <Text style={styles.predictText}>Analyzing …</Text>
                </>
              ) : (
                <>
                  <Ionicons name="sparkles" size={20} color="#fff" style={{ marginRight: 8 }} />
                  <Text style={styles.predictText}>Get Crop Recommendation</Text>
                </>
              )}
            </LinearGradient>
          </TouchableOpacity>

          <View style={{ height: SPACING.xxl }} />
        </ScrollView>
      </View>
    </TouchableWithoutFeedback>
  );
}

const styles = StyleSheet.create({
  container:     { flex: 1, backgroundColor: COLORS.background },

  header: {
    paddingTop: 20,
    paddingBottom: SPACING.lg,
    paddingHorizontal: SPACING.lg,
  },
  headerTitle:   { fontSize: 22, fontWeight: "800", color: "#fff" },
  headerSub:     { fontSize: 12, color: COLORS.accent, marginTop: 4 },

  scroll:        { flex: 1 },
  scrollContent: { padding: SPACING.md },

  // Field card
  fieldCard: {
    backgroundColor: COLORS.surface,
    borderRadius: RADIUS.md,
    padding: SPACING.md,
    marginBottom: SPACING.sm,
    borderWidth: 1,
    borderColor: COLORS.border,
    ...SHADOW.small,
  },
  fieldHeader:   { flexDirection: "row", alignItems: "center", marginBottom: 4 },
  fieldIconWrap: {
    width: 28, height: 28, borderRadius: 6,
    backgroundColor: COLORS.primaryDark,
    justifyContent: "center", alignItems: "center",
    marginRight: SPACING.sm,
  },
  fieldLabel:    { flex: 1, fontSize: 13, fontWeight: "700", color: COLORS.textPrimary },
  valueBadge:    {
    backgroundColor: COLORS.primaryDark,
    paddingHorizontal: 10, paddingVertical: 3,
    borderRadius: RADIUS.full,
  },
  valueText:     { fontSize: 12, color: COLORS.accent, fontWeight: "700" },
  fieldDesc:     { fontSize: 11, color: COLORS.textMuted, marginBottom: SPACING.sm, lineHeight: 16 },

  slider:        { width: "100%", height: 36 },

  rangeRow:      { flexDirection: "row", justifyContent: "space-between" },
  rangeText:     { fontSize: 10, color: COLORS.textMuted },

  // City input
  cityInput: {
    backgroundColor: COLORS.surfaceElevated,
    borderRadius: RADIUS.sm,
    borderWidth: 1,
    borderColor: COLORS.border,
    paddingHorizontal: SPACING.md,
    paddingVertical: 10,
    color: COLORS.textPrimary,
    fontSize: 14,
    marginTop: SPACING.sm,
  },

  // Predict button
  predictBtn: {
    marginTop: SPACING.lg,
    borderRadius: RADIUS.md,
    overflow: "hidden",
    ...SHADOW.large,
  },
  predictBtnDisabled: { opacity: 0.6 },
  predictGradient: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 16,
  },
  predictText: { color: "#fff", fontSize: 15, fontWeight: "700" },
});
