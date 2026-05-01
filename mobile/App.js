// App.js
// ──────────────────────────────────────────────────────────────────────────────
// Root of the React Native app.
// Sets up the navigation stack and global theme.

import "react-native-gesture-handler";   // Must be the very first import!
import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";

import HomeScreen    from "./screens/HomeScreen";
import PredictScreen from "./screens/PredictScreen";
import ResultScreen  from "./screens/ResultScreen";
import { COLORS }   from "./constants/theme";

// createStackNavigator returns a Navigator + Screen pair
const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          // Hide the default header – each screen draws its own header
          headerShown: false,
          // Slide-in animation
          cardStyleInterpolator: ({ current, layouts }) => ({
            cardStyle: {
              transform: [
                {
                  translateX: current.progress.interpolate({
                    inputRange:  [0, 1],
                    outputRange: [layouts.screen.width, 0],
                  }),
                },
              ],
            },
          }),
          cardStyle: { backgroundColor: COLORS.background },
        }}
      >
        <Stack.Screen name="Home"    component={HomeScreen}    />
        <Stack.Screen name="Predict" component={PredictScreen} />
        <Stack.Screen name="Result"  component={ResultScreen}  />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
