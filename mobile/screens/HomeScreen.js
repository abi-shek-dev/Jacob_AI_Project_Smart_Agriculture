// screens/HomeScreen.js
// ──────────────────────────────────────────────────────────────────────────────
// Landing screen: shows a hero banner, brief description, and a CTA button.
// This is the first screen the user sees when they open the app.

import React, { useEffect, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  StatusBar,
  ScrollView,
} from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import { COLORS, SPACING, RADIUS, SHADOW } from "../constants/theme";

// ── Feature card data (shown on the home screen) ─────────────────────────────
const FEATURE_CARDS = [
  {
    icon: "leaf",
    title: "AI Crop Prediction",
    desc: "Random Forest model trained on 2,200+ soil samples.",
  },
  {
    icon: "analytics",
    title: "SHAP Explanations",
    desc: "Understand why the AI made its recommendation.",
  },
  {
    icon: "partly-sunny",
    title: "Live Weather",
    desc: "Auto-fills temperature & humidity via OpenWeatherMap.",
  },
];

export default function HomeScreen({ navigation }) {
  // ── Entrance animations ───────────────────────────────────────────────────
  const fadeAnim  = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(40)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim,  { toValue: 1, duration: 800, useNativeDriver: true }),
      Animated.timing(slideAnim, { toValue: 0, duration: 800, useNativeDriver: true }),
    ]).start();
  }, []);

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={COLORS.primaryDark} />

      {/* ── Hero gradient banner ──────────────────────────────────────────── */}
      <LinearGradient
        colors={[COLORS.primaryDark, COLORS.primary, COLORS.primaryLight]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.hero}
      >
        <Animated.View style={{ opacity: fadeAnim, transform: [{ translateY: slideAnim }] }}>
          {/* Large leaf icon */}
          <View style={styles.iconCircle}>
            <Ionicons name="leaf" size={52} color={COLORS.accentWarm} />
          </View>

          <Text style={styles.heroTitle}>Smart Agriculture</Text>
          <Text style={styles.heroSubtitle}>AI Crop Recommendation System</Text>
          <Text style={styles.heroDesc}>
            Enter your soil data and get an AI-powered crop recommendation
            with full explainability.
          </Text>
        </Animated.View>
      </LinearGradient>

      {/* ── Feature cards ────────────────────────────────────────────────── */}
      <ScrollView contentContainerStyle={styles.body} showsVerticalScrollIndicator={false}>
        <Text style={styles.sectionLabel}>WHAT THIS APP DOES</Text>

        {FEATURE_CARDS.map((card, idx) => (
          <Animated.View
            key={idx}
            style={[
              styles.card,
              {
                opacity: fadeAnim,
                transform: [{ translateY: slideAnim }],
              },
            ]}
          >
            <View style={styles.cardIconWrap}>
              <Ionicons name={card.icon} size={26} color={COLORS.primaryLight} />
            </View>
            <View style={styles.cardText}>
              <Text style={styles.cardTitle}>{card.title}</Text>
              <Text style={styles.cardDesc}>{card.desc}</Text>
            </View>
          </Animated.View>
        ))}

        {/* ── CTA Button ──────────────────────────────────────────────────── */}
        <TouchableOpacity
          style={styles.ctaButton}
          onPress={() => navigation.navigate("Predict")}
          activeOpacity={0.85}
        >
          <LinearGradient
            colors={[COLORS.primaryLight, COLORS.primary]}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.ctaGradient}
          >
            <Ionicons name="flask" size={20} color="#fff" style={{ marginRight: 8 }} />
            <Text style={styles.ctaText}>Start Prediction</Text>
          </LinearGradient>
        </TouchableOpacity>

        {/* Spacer at bottom */}
        <View style={{ height: SPACING.xl }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },

  // Hero
  hero: {
    paddingTop: 60,
    paddingBottom: 40,
    paddingHorizontal: SPACING.lg,
    alignItems: "center",
  },
  iconCircle: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: "rgba(255,255,255,0.12)",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: SPACING.md,
    borderWidth: 2,
    borderColor: "rgba(255,255,255,0.25)",
  },
  heroTitle: {
    fontSize: 30,
    fontWeight: "800",
    color: "#fff",
    textAlign: "center",
  },
  heroSubtitle: {
    fontSize: 14,
    color: COLORS.accent,
    textAlign: "center",
    letterSpacing: 1.2,
    marginTop: 4,
    textTransform: "uppercase",
  },
  heroDesc: {
    fontSize: 13,
    color: "rgba(255,255,255,0.75)",
    textAlign: "center",
    marginTop: SPACING.sm,
    lineHeight: 20,
    maxWidth: 280,
  },

  // Body
  body: {
    padding: SPACING.md,
  },
  sectionLabel: {
    fontSize: 11,
    color: COLORS.textMuted,
    letterSpacing: 1.5,
    fontWeight: "700",
    marginTop: SPACING.sm,
    marginBottom: SPACING.sm,
  },

  // Feature cards
  card: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: COLORS.surface,
    borderRadius: RADIUS.md,
    padding: SPACING.md,
    marginBottom: SPACING.sm,
    borderWidth: 1,
    borderColor: COLORS.border,
    ...SHADOW.small,
  },
  cardIconWrap: {
    width: 48,
    height: 48,
    borderRadius: RADIUS.sm,
    backgroundColor: COLORS.primaryDark,
    justifyContent: "center",
    alignItems: "center",
    marginRight: SPACING.md,
  },
  cardText: { flex: 1 },
  cardTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: COLORS.textPrimary,
    marginBottom: 2,
  },
  cardDesc: {
    fontSize: 12,
    color: COLORS.textSecondary,
    lineHeight: 17,
  },

  // CTA button
  ctaButton: {
    marginTop: SPACING.lg,
    borderRadius: RADIUS.md,
    overflow: "hidden",
    ...SHADOW.large,
  },
  ctaGradient: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 16,
    paddingHorizontal: SPACING.lg,
  },
  ctaText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
});
