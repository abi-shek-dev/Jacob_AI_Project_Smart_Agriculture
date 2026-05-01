// screens/ResultScreen.js
// ──────────────────────────────────────────────────────────────────────────────
// Displays the prediction result including:
//   • Recommended crop with confidence badge
//   • Bar chart of Feature Importance (built-in)
//   • SHAP values bar chart (per-prediction explanation)
//   • Human-readable explanation text
//   • Option to go back and try different inputs

import React, { useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Animated,
  Dimensions,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { COLORS, SPACING, RADIUS, SHADOW } from "../constants/theme";

const { width: SCREEN_W } = Dimensions.get("window");

// Readable names for the 7 features
const FEATURE_LABELS = {
  N:           "Nitrogen",
  P:           "Phosphorus",
  K:           "Potassium",
  temperature: "Temperature",
  humidity:    "Humidity",
  ph:          "Soil pH",
  rainfall:    "Rainfall",
};

// ── Horizontal bar chart component ───────────────────────────────────────────
function BarChart({ data, title, positiveColor, negativeColor, showSigned }) {
  /**
   * data = [{label, value}]
   * positiveColor / negativeColor: for SHAP (which can be negative)
   * showSigned: if true, bars to left = negative contribution
   */
  const maxAbs = Math.max(...data.map((d) => Math.abs(d.value)), 0.001);
  const BAR_MAX_W = SCREEN_W - 180;  // max bar width in pixels

  return (
    <View style={chart.container}>
      <Text style={chart.title}>{title}</Text>
      {data.map((item, idx) => {
        const pct    = Math.abs(item.value) / maxAbs;
        const barW   = pct * BAR_MAX_W;
        const isPos  = item.value >= 0;
        const color  = showSigned
          ? (isPos ? positiveColor || COLORS.primaryLight : negativeColor || COLORS.danger)
          : COLORS.chart[idx % COLORS.chart.length];

        return (
          <View key={idx} style={chart.row}>
            <Text style={chart.label} numberOfLines={1}>
              {FEATURE_LABELS[item.label] || item.label}
            </Text>
            <View style={chart.barWrap}>
              <View style={[chart.bar, { width: barW, backgroundColor: color }]} />
              <Text style={chart.barValue}>
                {showSigned && item.value > 0 ? "+" : ""}
                {item.value.toFixed(3)}
              </Text>
            </View>
          </View>
        );
      })}
    </View>
  );
}

const chart = StyleSheet.create({
  container: { marginBottom: SPACING.md },
  title:     {
    fontSize: 13, fontWeight: "700", color: COLORS.textPrimary,
    marginBottom: SPACING.sm, letterSpacing: 0.5,
  },
  row:       { flexDirection: "row", alignItems: "center", marginBottom: 7 },
  label:     { width: 88, fontSize: 11, color: COLORS.textSecondary, flexShrink: 0 },
  barWrap:   { flex: 1, flexDirection: "row", alignItems: "center" },
  bar:       { height: 12, borderRadius: 6, minWidth: 4 },
  barValue:  { fontSize: 10, color: COLORS.textMuted, marginLeft: 6 },
});

// ── Main result screen ────────────────────────────────────────────────────────
export default function ResultScreen({ route, navigation }) {
  const { result, inputs } = route.params;
  const fadeAnim  = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.85)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim,  { toValue: 1, duration: 600, useNativeDriver: true }),
      Animated.spring(scaleAnim, { toValue: 1, friction: 5,   useNativeDriver: true }),
    ]).start();
  }, []);

  // Prepare chart data
  const fiData = Object.entries(result.feature_importance || {})
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value);

  const shapData = Object.entries(result.shap_values || {})
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

  const confidence = result.confidence_pct ?? 0;
  const confColor  =
    confidence >= 80 ? COLORS.success :
    confidence >= 55 ? COLORS.warning : COLORS.danger;

  return (
    <View style={styles.container}>
      <StatusBar style="light" backgroundColor={COLORS.primaryDark} />

      {/* ── Header ───────────────────────────────────────────────────────── */}
      <LinearGradient colors={[COLORS.primaryDark, COLORS.primary]} style={styles.header}>
        <TouchableOpacity
          style={styles.backBtn}
          onPress={() => navigation.goBack()}
        >
          <Ionicons name="arrow-back" size={20} color="#fff" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Recommendation Result</Text>
      </LinearGradient>

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>

        {/* ── Hero crop card ──────────────────────────────────────────────── */}
        <Animated.View style={{ opacity: fadeAnim, transform: [{ scale: scaleAnim }] }}>
          <LinearGradient
            colors={[COLORS.primary, COLORS.primaryDark]}
            style={styles.cropCard}
          >
            <Ionicons name="leaf" size={48} color={COLORS.accent} />
            <Text style={styles.cropName}>{result.recommended_crop?.toUpperCase()}</Text>
            <Text style={styles.cropSub}>Recommended Crop</Text>

            {/* Confidence badge */}
            <View style={[styles.confBadge, { backgroundColor: confColor + "33" }]}>
              <Text style={[styles.confText, { color: confColor }]}>
                {confidence.toFixed(1)}% confidence
              </Text>
            </View>

            {/* Model & weather info pills */}
            <View style={styles.pillRow}>
              <View style={styles.pill}>
                <Ionicons name="hardware-chip" size={11} color={COLORS.textMuted} />
                <Text style={styles.pillText}>{result.model_used}</Text>
              </View>
              {result.weather_used && (
                <View style={[styles.pill, { borderColor: COLORS.info }]}>
                  <Ionicons name="cloud" size={11} color={COLORS.info} />
                  <Text style={[styles.pillText, { color: COLORS.info }]}>Live Weather Used</Text>
                </View>
              )}
            </View>
          </LinearGradient>
        </Animated.View>

        {/* ── Explanation text ────────────────────────────────────────────── */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="bulb" size={16} color={COLORS.warning} />
            <Text style={styles.sectionTitle}>Why This Crop?</Text>
          </View>
          <Text style={styles.explanationText}>{result.explanation_text}</Text>
        </View>

        {/* ── Feature Importance chart ────────────────────────────────────── */}
        {fiData.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="bar-chart" size={16} color={COLORS.primaryLight} />
              <Text style={styles.sectionTitle}>Feature Importance (Global)</Text>
            </View>
            <Text style={styles.sectionDesc}>
              How much each soil property influences the model's decisions overall.
              Higher = more important.
            </Text>
            <BarChart
              data={fiData}
              title=""
              showSigned={false}
            />
          </View>
        )}

        {/* ── SHAP chart ─────────────────────────────────────────────────── */}
        {shapData.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="analytics" size={16} color={COLORS.info} />
              <Text style={styles.sectionTitle}>SHAP Explanation (This Prediction)</Text>
            </View>
            <Text style={styles.sectionDesc}>
              🟢 Green bars pushed the prediction toward {result.recommended_crop}.{"\n"}
              🔴 Red bars pushed against it.
            </Text>
            <BarChart
              data={shapData}
              title=""
              showSigned={true}
              positiveColor={COLORS.success}
              negativeColor={COLORS.danger}
            />
          </View>
        )}

        {/* ── Input summary ───────────────────────────────────────────────── */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Ionicons name="list" size={16} color={COLORS.textSecondary} />
            <Text style={styles.sectionTitle}>Your Input Values</Text>
          </View>
          <View style={styles.inputGrid}>
            {Object.entries(inputs).map(([key, val]) => (
              <View key={key} style={styles.inputChip}>
                <Text style={styles.inputKey}>{FEATURE_LABELS[key] || key}</Text>
                <Text style={styles.inputVal}>{Number(val).toFixed(1)}</Text>
              </View>
            ))}
          </View>
        </View>

        {/* ── Try Again button ────────────────────────────────────────────── */}
        <TouchableOpacity
          style={styles.retryBtn}
          onPress={() => navigation.navigate("Predict")}
          activeOpacity={0.85}
        >
          <Ionicons name="refresh" size={18} color={COLORS.primaryLight} />
          <Text style={styles.retryText}>Try Different Values</Text>
        </TouchableOpacity>

        <View style={{ height: SPACING.xxl }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container:      { flex: 1, backgroundColor: COLORS.background },

  header: {
    paddingTop: 20,
    paddingBottom: SPACING.md,
    paddingHorizontal: SPACING.md,
    flexDirection: "row",
    alignItems: "center",
  },
  backBtn: {
    width: 36, height: 36, borderRadius: 18,
    backgroundColor: "rgba(255,255,255,0.15)",
    justifyContent: "center", alignItems: "center",
    marginRight: SPACING.sm,
  },
  headerTitle: { fontSize: 18, fontWeight: "700", color: "#fff" },

  scroll: { padding: SPACING.md },

  // Crop hero card
  cropCard: {
    borderRadius: RADIUS.lg,
    padding: SPACING.lg,
    alignItems: "center",
    marginBottom: SPACING.md,
    ...SHADOW.large,
  },
  cropName: {
    fontSize: 32, fontWeight: "900", color: "#fff",
    letterSpacing: 2, marginTop: SPACING.sm,
  },
  cropSub:  { fontSize: 12, color: COLORS.accent, letterSpacing: 1.5, marginTop: 2 },
  confBadge: {
    marginTop: SPACING.sm,
    paddingHorizontal: 14, paddingVertical: 5,
    borderRadius: RADIUS.full,
    borderWidth: 1,
  },
  confText: { fontSize: 13, fontWeight: "700" },
  pillRow:  { flexDirection: "row", gap: 8, marginTop: SPACING.sm },
  pill: {
    flexDirection: "row", alignItems: "center", gap: 4,
    paddingHorizontal: 10, paddingVertical: 4,
    borderRadius: RADIUS.full,
    borderWidth: 1, borderColor: COLORS.border,
    backgroundColor: "rgba(0,0,0,0.2)",
  },
  pillText: { fontSize: 10, color: COLORS.textMuted },

  // Sections
  section: {
    backgroundColor: COLORS.surface,
    borderRadius: RADIUS.md,
    padding: SPACING.md,
    marginBottom: SPACING.sm,
    borderWidth: 1,
    borderColor: COLORS.border,
    ...SHADOW.small,
  },
  sectionHeader: {
    flexDirection: "row", alignItems: "center", gap: 6,
    marginBottom: SPACING.sm,
  },
  sectionTitle: { fontSize: 13, fontWeight: "700", color: COLORS.textPrimary },
  sectionDesc:  {
    fontSize: 11, color: COLORS.textMuted, lineHeight: 16,
    marginBottom: SPACING.sm,
  },

  // Explanation
  explanationText: {
    fontSize: 13, color: COLORS.textSecondary, lineHeight: 20,
  },

  // Input grid
  inputGrid: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  inputChip: {
    backgroundColor: COLORS.surfaceElevated,
    borderRadius: RADIUS.sm,
    paddingHorizontal: 10, paddingVertical: 6,
    alignItems: "center", minWidth: 80,
  },
  inputKey: { fontSize: 10, color: COLORS.textMuted, marginBottom: 2 },
  inputVal: { fontSize: 13, fontWeight: "700", color: COLORS.textPrimary },

  // Retry button
  retryBtn: {
    flexDirection: "row", alignItems: "center", justifyContent: "center",
    gap: 8, marginTop: SPACING.md,
    borderWidth: 1.5, borderColor: COLORS.primaryLight,
    borderRadius: RADIUS.md, paddingVertical: 14,
  },
  retryText: { fontSize: 14, color: COLORS.primaryLight, fontWeight: "700" },
});
